# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from astropy.io import fits
import datetime
import json
import numpy as np
import os
import sys

from .maskfromflat import maskfromflat
from .retrieve_calibration import retrieve_calibration
from .signature import getkey_from_signature
from .signature import signature_string
from .statsumm import statsumm
from .tologfile import ToLogFile
from .version import version

from filabres import LISTDIR


def run_calibration_step(redustep, setupdata, list_of_nights,
                         instconf, force, verbose=False, debug=False):
    """
    Execute reduction step.

    Parameters
    ==========
    redustep : str
        Reduction step to be executed.
    setupdata : dict
        Setup data stored as a Python dictionary.
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    force : bool
        If True, recompute reduction of calibration images.
    verbose : bool
        If True, display intermediate information.
    debug : bool
        Display additional debugging information.
    """

    datadir = setupdata['datadir']
    instrument = instconf['instname']

    # set the results database: note that for calibration images, this
    # database is stored in a single JSON file in the current directory
    databasefile = 'filabres_db_{}_{}.json'.format(instrument, redustep)
    try:
        with open(databasefile) as jfile:
            database = json.load(jfile)
    except FileNotFoundError:
        database = {}
    if verbose:
        print('\nResults database set to {}'.format(databasefile))

    # check for subdirectory in current directory to store results
    if os.path.isdir(redustep):
        if verbose:
            print('\nSubdirectory {} found'.format(redustep))
    else:
        if verbose:
            print('\nSubdirectory {} not found. Creating it!'.format(redustep))
        os.makedirs(redustep)

    # set maxtimespan_hours
    maxtimespan_hours = instconf['imagetypes'][redustep]['maxtimespan_hours']
    if verbose:
        print('maxtimespan_hours: {}'.format(maxtimespan_hours))

    # define signature keys
    signaturekeys = instconf['imagetypes'][redustep]['signature']

    # loop in night
    for inight, night in enumerate(list_of_nights):

        print('\n* Working with night {} ({}/{})'.format(night, inight + 1, len(list_of_nights)))

        # read local image database for current night
        jsonfname = LISTDIR + night + '/imagedb_'
        jsonfname += instconf['instname'] + '.json'
        if verbose:
            print('Reading file {}'.format(jsonfname))
        try:
            with open(jsonfname) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            print('ERROR: file {} not found'.format(jsonfname))
            msg = 'Try using -rs initialize'
            raise SystemError(msg)

        # check version of instrument configuration
        if instconf['version'] != imagedb['metainfo']['instconf']['version']:
            msg = 'ERROR: different versions of instrument configuration'
            raise SystemError(msg)

        # select images of the requested type
        list_of_images = list(imagedb[redustep].keys())
        list_of_images.sort()
        nlist_of_images = len(list_of_images)
        if verbose:
            print('Number of {} images found {}'.format(redustep, nlist_of_images))

        if nlist_of_images > 0:

            # create subdirectory to store results for current night
            nightdir = redustep + '/' + night
            if os.path.isdir(nightdir):
                if verbose:
                    print('Subdirectory {} found'.format(nightdir))
            else:
                if verbose:
                    print('Subdirectory {} not found. Creating it!'.format(nightdir))
                os.makedirs(nightdir)

            # determine number of different signatures
            list_of_signatures = []
            for fname in list_of_images:
                # signature of particular image
                imgsignature = dict()
                for keyword in signaturekeys:
                    imgsignature[keyword] = imagedb[redustep][fname][keyword]
                if len(list_of_signatures) == 0:
                    list_of_signatures.append(imgsignature)
                else:
                    signaturefound = False
                    for dumsignature in list_of_signatures:
                        if dumsignature == imgsignature:
                            signaturefound = True
                            break
                    if not signaturefound:
                        list_of_signatures.append(imgsignature)
            if verbose:
                nsignatures = len(list_of_signatures)
                print('Number of different signatures found:', nsignatures)

            # select images with a common signature and subdivide this
            # selection into blocks where the images are grouped within
            # the indicated timespan
            for isignature in range(len(list_of_signatures)):
                signature = list_of_signatures[isignature]
                images_with_fixed_signature = []
                for fname in list_of_images:
                    # signature of particular image
                    imgsignature = dict()
                    for keyword in signaturekeys:
                        imgsignature[keyword] = imagedb[redustep][fname][keyword]
                    if imgsignature == signature:
                        images_with_fixed_signature.append(datadir + night + '/' + fname)
                images_with_fixed_signature.sort()
                nfiles = len(images_with_fixed_signature)
                if nfiles == 0:
                    msg = 'ERROR: unexpected number of {} images = 0'.format(nfiles)
                    raise SystemError(msg)
                # dictionary indicating whether the images with this signature have been classified
                classified_images = dict()
                for fname in images_with_fixed_signature:
                    classified_images[fname] = False
                if verbose:
                    print('\nSignature ({}/{}):'.format(isignature+1, len(list_of_signatures)))
                    for key in signaturekeys:
                        print(' - {}: {}'.format(key, signature[key]))
                    print('Total number of images with this signature:', len(images_with_fixed_signature))
                    if debug:
                        for fname in images_with_fixed_signature:
                            print(fname, end=' ')
                        print()

                images_pending = True
                while images_pending:
                    # select images with the same signature and within the
                    # specified maximum time span
                    imgblock = []
                    mean_mjdobs = 0.0
                    if maxtimespan_hours == 0:
                        # reduce individual images
                        for fname in classified_images:
                            if not classified_images[fname]:
                                basename = os.path.basename(fname)
                                if debug:
                                    print(' - {}'.format(fname))
                                t = imagedb[redustep][basename]['MJD-OBS']
                                mean_mjdobs += t
                                imgblock.append(fname)
                                break
                    else:
                        t0 = None
                        for fname in classified_images:
                            if not classified_images[fname]:
                                basename = os.path.basename(fname)
                                t = imagedb[redustep][basename]['MJD-OBS']
                                if len(imgblock) == 0:
                                    imgblock.append(fname)
                                    t0 = imagedb[redustep][basename]['MJD-OBS']
                                    mean_mjdobs += t0
                                    if debug:
                                        print(' - {}'.format(fname))
                                else:
                                    if abs(t-t0) < maxtimespan_hours/24:
                                        if debug:
                                            print(' - {}'.format(fname))
                                        imgblock.append(fname)
                                        mean_mjdobs += t
                    imgblock.sort()
                    nfiles = len(imgblock)
                    originf = [os.path.basename(dum) for dum in imgblock]
                    mean_mjdobs /= nfiles

                    # define output FITS file using the file name of the first
                    # image in the block (appending the _red suffix)
                    output_fname = nightdir + '/' + redustep + '_'
                    dumfile = os.path.basename(imgblock[0])
                    output_fname += dumfile[:-5]
                    output_mname = output_fname + '_mask.fits'
                    output_lname = output_fname + '_red.log'
                    output_fname += '_red.fits'
                    execute_reduction = True
                    if os.path.exists(output_fname) and not force:
                        execute_reduction = False
                        print('File {} already exists: skipping reduction.'.format(output_fname))

                    if execute_reduction:
                        # generate string with signature values
                        ssig = signature_string(signaturekeys, signature)
                        logfile = ToLogFile(basename=output_lname, verbose=verbose)
                        datetime_ini = datetime.datetime.now()
                        logfile.print('---', f=True)
                        logfile.print('-> Reduction starts at.: {}'.format(datetime_ini))
                        logfile.print('Working with signature {}'.format(ssig), f=True)
                        logfile.print('-> Number of images with expected signature '
                                      'and within time span: {}'.format(nfiles))
                        for fname in imgblock:
                            logfile.print(' - {}'.format(fname))
                        logfile.print('-> Output fname will be: {}'.format(output_fname))

                        # note: the following step must be performed before
                        # saving the combined image; otherwise, the cleanup
                        # procedure will delete the just created combined image
                        if redustep not in database:
                            database[redustep] = dict()
                        if 'signaturekeys' not in database:
                            database['signaturekeys'] = signaturekeys
                        else:
                            if signaturekeys != database['signaturekeys']:
                                msg = 'ERROR: signaturekeys have changed when reducing {} images'.format(redustep)
                                raise SystemError(msg)

                        if ssig not in database[redustep]:
                            # update main database with new signature if not present
                            database[redustep][ssig] = dict()
                        else:
                            # check that there is not a combined image using any
                            # of the individual images of imgblock: otherwise,
                            # some entries of the main database must be removed
                            # and the associated reduced images deleted
                            if len(database[redustep][ssig]) > 0:
                                mjdobs_to_be_deleted = []
                                for mjdobs in database[redustep][ssig]:
                                    old_originf = database[redustep][ssig][mjdobs]['originf']
                                    # is there a conflict?
                                    conflict = list(set(originf) & set(old_originf))
                                    if len(conflict) > 0:
                                        mjdobs_to_be_deleted.append(mjdobs)
                                        fname = database[redustep][ssig][mjdobs]['fname']
                                        mname = database[redustep][ssig][mjdobs]['mname']
                                        if os.path.exists(fname):
                                            logfile.print('Deleting {}'.format(fname))
                                            os.remove(fname)
                                        if os.path.exists(mname):
                                            logfile.print('Deleting {}'.format(mname))
                                            os.remove(mname)
                                for mjdobs in mjdobs_to_be_deleted:
                                    logfile.print('WARNING: deleting previous database entry:'
                                                  ' {} --> {} --> {}'.format(redustep, ssig, mjdobs))
                                    del database[redustep][ssig][mjdobs]

                        # declare temporary cube to store the images to be combined
                        naxis1 = getkey_from_signature(signature, 'NAXIS1')
                        naxis2 = getkey_from_signature(signature, 'NAXIS2')
                        image3d = np.zeros((nfiles, naxis2, naxis1), dtype=float)
                        exptime = np.zeros(nfiles, dtype=float)

                        # output file name
                        output_header = None

                        # store images in temporary data cube
                        for i in range(nfiles):
                            fname = imgblock[i]
                            basename = os.path.basename(fname)
                            exptime[i] = imagedb[redustep][basename]['EXPTIME']
                            with fits.open(fname) as hdulist:
                                image_header = hdulist[0].header
                                image_data = hdulist[0].data
                            if i == 0:
                                output_header = image_header
                                output_header.add_history("---")
                                output_header.add_history('Using filabres v.{}'.format(version))
                                output_header.add_history('Date: ' + str(datetime.datetime.utcnow().isoformat()))
                                output_header.add_history(str(sys.argv))
                                # avoid warning when saving FITS
                                if 'BLANK' in output_header:
                                    del output_header['BLANK']
                                # check for modified keywords when initializing
                                # the image databases
                                for keyword in instconf['masterkeywords']:
                                    val2 = imagedb[redustep][basename][keyword]
                                    if keyword in output_header:
                                        val1 = output_header[keyword]
                                        if val1 != val2:
                                            output_header[keyword] = val2
                                            logfile.print('WARNING: {} changed from {} to {}'.format(
                                                keyword, val1, val2))
                                    else:
                                        output_header[keyword] = val2
                                        logfile.print('WARNING: missing {} set to {}'.format(keyword, val2))
                                output_header.add_history('Using {} images to compute {}:'.format(nfiles, redustep))
                            image3d[i, :, :] += image_data
                            output_header.add_history(basename)
                        output_header.add_history('Signature:')
                        for key in signature:
                            output_header.add_history(' - {}: {}'.format(key, signature[key]))

                        # combine images according to their type
                        ierr_bias = None
                        delta_mjd_bias = None
                        bias_fname = None
                        ierr_flat = None
                        # ---------------------------------------------------------
                        if redustep == 'bias':
                            # median combination
                            image2d = np.median(image3d, axis=0)
                            output_header.add_history('Combination method: median')
                            # compute statistical analysis and update the image header
                            image2d_statsumm = statsumm(
                                image2d=image2d,
                                header=output_header,
                                redustep=redustep,
                                rm_nan=True
                            )
                            mask2d = None
                        # ---------------------------------------------------------
                        elif redustep == 'flat-imaging':
                            ierr_flat = 0
                            basicreduction = instconf['imagetypes'][redustep]['basicreduction']
                            if basicreduction:
                                mjdobs = output_header['MJD-OBS']
                                # retrieve master bias
                                ierr_bias, delta_mjd_bias, image2d_bias, bias_fname = retrieve_calibration(
                                        instrument, 'bias', signature, mjdobs, logfile=logfile)
                                # subtract bias
                                output_header.add_history('Subtracting master bias:')
                                output_header.add_history(bias_fname)
                                if debug:
                                    logfile.print('bias level:', np.median(image2d_bias))
                                for i in range(nfiles):
                                    image3d[i, :, :] -= image2d_bias
                                # stack all the images for the computation of a single mask
                                # for all the individual images
                                image2d = np.sum(image3d, axis=0)
                                mediansignal = np.median(image2d)
                                if mediansignal > 0:
                                    image2d /= mediansignal
                                else:
                                    msg = 'WARNING: mediansignal={} is not > 0'.format(mediansignal)
                                    logfile.print(msg)
                                    ierr_flat = 1
                                mask2d = maskfromflat(image2d)
                                for i in range(nfiles):
                                    # perform statistical analysis in useful region
                                    image2d_statsumm = statsumm(image2d=image3d[i, :, :], mask2d=mask2d, rm_nan=True)
                                    # normalize by the median value in the useful region
                                    mediansignal = image2d_statsumm['QUANT500']
                                    logfile.print('Median value in frame #{}/{}: {}'.format(i+1, nfiles, mediansignal))
                                    if mediansignal > 0:
                                        image3d[i, :, :] /= mediansignal
                                    else:
                                        msg = 'WARNING: mediansignal={} is not > 0'.format(mediansignal)
                                        logfile.print(msg)
                                        ierr_flat = 1
                            else:
                                msg = 'WARNING: skipping basic reduction when generating {}'.format(output_fname)
                                logfile.print(msg)
                            # median combination of normalized images
                            image2d = np.median(image3d, axis=0)
                            # set to 1.0 pixels with values <= 0
                            image2d[image2d <= 0.0] = 1.0
                            output_header.add_history('Combination method: median of normalized images')
                            # perform statistical analysis in the useful region and update the image header
                            mask2d = maskfromflat(image2d)
                            image2d_statsumm = statsumm(
                                image2d=image2d,
                                mask2d=mask2d,
                                header=output_header,
                                redustep=redustep,
                                rm_nan=True
                            )
                        # ---------------------------------------------------------
                        else:
                            msg = '* ERROR: combination of {} not implemented yet'.format(redustep)
                            raise SystemError(msg)

                        # save result
                        hdu = fits.PrimaryHDU(image2d, output_header)
                        hdu.writeto(output_fname, overwrite=True)
                        logfile.print('Creating {}'.format(output_fname), f=True)
                        # save mask
                        if mask2d is not None:
                            hdu = fits.PrimaryHDU(mask2d, output_header)
                            hdu.writeto(output_mname, overwrite=True)
                            logfile.print('Creating {}'.format(output_mname), f=True)

                        # update database with result using the mean MJD-OBS of
                        # the combined images as index
                        mjdobs = '{:.5f}'.format(mean_mjdobs)
                        database[redustep][ssig][mjdobs] = dict()
                        database[redustep][ssig][mjdobs]['night'] = night
                        database[redustep][ssig][mjdobs]['signature'] = signature
                        database[redustep][ssig][mjdobs]['fname'] = output_fname
                        database[redustep][ssig][mjdobs]['mname'] = output_mname
                        database[redustep][ssig][mjdobs]['lname'] = output_lname
                        database[redustep][ssig][mjdobs]['statsumm'] = image2d_statsumm
                        dumdict = dict()
                        for keyword in instconf['masterkeywords']:
                            dumdict[keyword] = output_header[keyword]
                        database[redustep][ssig][mjdobs]['masterkeywords'] = dumdict
                        database[redustep][ssig][mjdobs]['norigin'] = nfiles
                        database[redustep][ssig][mjdobs]['originf'] = originf
                        if ierr_bias is not None:
                            database[redustep][ssig][mjdobs]['ierr_bias'] = ierr_bias
                        if delta_mjd_bias is not None:
                            database[redustep][ssig][mjdobs]['delta_mjd_bias'] = delta_mjd_bias
                        if bias_fname is not None:
                            database[redustep][ssig][mjdobs]['bias_fname'] = bias_fname
                        if ierr_flat is not None:
                            database[redustep][ssig][mjdobs]['ierr_flat'] = ierr_flat

                        # close logfile
                        datetime_end = datetime.datetime.now()
                        logfile.print('Creating {}'.format(logfile.fname))
                        logfile.print('-> Reduction ends at...: {}'.format(datetime_end))
                        logfile.print('-> Time span...........: {}'.format(datetime_end - datetime_ini))
                        logfile.close()

                    # set to reduced status the images that have been reduced
                    for key in imgblock:
                        classified_images[key] = True

                    # check if there are still images with the selected
                    # signature pending to be reduced
                    images_pending = False
                    for key in classified_images:
                        if not classified_images[key]:
                            images_pending = True
                            break
        else:
            # skipping night (no images of sought type found)
            if verbose:
                print('No {} images found. Skipping night!'.format(redustep))

    # update results database
    with open(databasefile, 'w') as outfile:
        json.dump(database, outfile, indent=2)
