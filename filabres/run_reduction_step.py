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

from .cmdexecute import CmdExecute
from .maskfromflat import maskfromflat
from .retrieve_calibration import retrieve_calibration
from .run_astrometry import run_astrometry
from .signature import getkey_from_signature
from .statsumm import statsumm
from .tologfile import ToLogFile
from .version import version

from filabres import LISTDIR
SATURATION_LEVEL = 65000


def run_reduction_step(redustep, interactive, setupdata, list_of_nights, filename,
                       instconf, force, verbose=False, debug=False):
    """
    Execute reduction step.

    Parameters
    ==========
    redustep : str
        Reduction step to be executed.
    interactive : bool
        If True, enable interactive execution (e.g. plots,...).
    setupdata : dict
        Setup data stored as a Python dictionary.
    list_of_nights : list
        List of nights matching the selection filter.
    filename : str
        File name of the image to be reduced.
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

    if filename is not None:
        if filename.find('*') >= 0 or filename.find('?') >= 0:
            msg = 'ERROR: wildcards are not valid for --filename argument: {}'.format(filename)
            raise SystemError(msg)

    instrument = instconf['instname']

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
    if maxtimespan_hours != 0:
        msg = 'Unexpected maxtimespan_hours != 0 found: {}'.format(maxtimespan_hours)
        raise SystemError(msg)

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
        # check if a single image should be processed
        if filename is not None:
            if filename in list_of_images:
                list_of_images = [filename]
            else:
                print('WARNING: image {} not found in night {}'.format(filename, night))
                list_of_images = []
        nlist_of_images = len(list_of_images)
        if verbose:
            print('Number of {} images found: {}'.format(redustep, nlist_of_images))

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

            # execute reduction for all the selected files
            for ifname, fname in enumerate(list_of_images):
                # define ToLogFile object
                logfile = ToLogFile(workdir=nightdir, basename='reduction.log', verbose=verbose)
                logfile.print('\nBasic reduction of {}'.format(fname))

                # set the expected database: note that for science images, this
                # database is stored as an independent JSON file for each night
                # which is read and updated after the reduction of every single
                # image
                databasefile = nightdir + '/'
                databasefile += 'filabres_db_{}_{}.json'.format(instrument, redustep)
                try:
                    with open(databasefile) as jfile:
                        database = json.load(jfile)
                except FileNotFoundError:
                    database = {}
                logfile.print('\nResults database set to {}'.format(databasefile))

                # define input file name
                input_fname = datadir + night + '/' + fname
                # define output FITS file name
                output_fname = nightdir + '/' + redustep + '_'
                output_fname += fname[:-5] + '_red.fits'
                execute_reduction = True
                logfile.print('---', f=True)
                logfile.print('-> Working with file {} ({}/{})  [Night {}/{}]'.format(
                    fname, ifname + 1, len(list_of_images), inight + 1, len(list_of_nights)), f=True)
                logfile.print('-> Input file name is......: {}'.format(input_fname), f=True)
                logfile.print('-> Output file name will be: {}'.format(output_fname), f=True)
                datetime_ini = datetime.datetime.now()
                logfile.print('-> Reduction starts at.....: {}'.format(datetime_ini), f=True)
                if os.path.exists(output_fname) and not force:
                    execute_reduction = False
                    logfile.print('File {} already exists: skipping reduction.'.format(output_fname), f=True)

                if execute_reduction:
                    # signature of particular image
                    imgsignature = dict()
                    for keyword in signaturekeys:
                        imgsignature[keyword] = imagedb[redustep][fname][keyword]

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

                    # declare temporary cube to store the images to be combined
                    naxis1 = getkey_from_signature(imgsignature, 'NAXIS1')
                    naxis2 = getkey_from_signature(imgsignature, 'NAXIS2')
                    image2d_saturpix = np.zeros((naxis2, naxis1), dtype=np.bool)

                    with fits.open(input_fname) as hdulist:
                        image_header = hdulist[0].header
                        image2d = hdulist[0].data.astype(float)
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
                        val2 = imagedb[redustep][fname][keyword]
                        if keyword in output_header:
                            val1 = output_header[keyword]
                            if val1 != val2:
                                output_header[keyword] = val2
                                logfile.print('WARNING: {} changed from {} to {}'.format(keyword, val1, val2), f=True)
                        else:
                            output_header[keyword] = val2
                            logfile.print('WARNING: missing {} set to {}'.format(keyword, val2))
                    output_header.add_history('Creating {} file:'.format(redustep))
                    saturpix = np.where(image2d >= SATURATION_LEVEL)
                    image2d_saturpix[saturpix] = True
                    output_header.add_history(os.path.basename(fname))
                    output_header.add_history('Signature:')
                    for key in imgsignature:
                        output_header.add_history(' - {}: {}'.format(key, imgsignature[key]))

                    # combine images according to their type
                    # ---------------------------------------------------------
                    ierr_bias = None
                    delta_mjd_bias = None
                    bias_fname = None
                    ierr_flat = None
                    delta_mjd_flat = None
                    flat_fname = None
                    if redustep == 'science-imaging':
                        basicreduction = instconf['imagetypes'][redustep]['basicreduction']
                        if basicreduction:
                            mjdobs = output_header['MJD-OBS']
                            # retrieve and subtract bias
                            ierr_bias, delta_mjd_bias, image2d_bias, bias_fname = retrieve_calibration(
                                    instrument, 'bias', imgsignature, mjdobs, logfile=logfile)
                            output_header.add_history('Subtracting master bias:')
                            output_header.add_history(bias_fname)
                            if debug:
                                logfile.print('bias level: {}'.format(np.median(image2d_bias)), f=True)
                            image2d -= image2d_bias
                            # retrieve and divide by flatfield
                            ierr_flat, delta_mjd_flat, image2d_flat, flat_fname = retrieve_calibration(
                                    instrument, 'flat-imaging', imgsignature, mjdobs, logfile=logfile)
                            output_header.add_history('Applying master flatfield:')
                            output_header.add_history(flat_fname)
                            if debug:
                                logfile.print('flat level: {}'.format(np.median(image2d_flat)), f=True)
                            image2d /= image2d_flat
                            # generate useful region mask from flatfield
                            mask2d = maskfromflat(image2d_flat)
                            if debug:
                                logfile.print('masked pixels: {}/{}'.format(np.sum(mask2d == 0.0), naxis1 * naxis2),
                                              f=True)
                        else:
                            msg = 'WARNING: skipping basic reduction working with file {}'.format(fname)
                            logfile.print(msg)
                            mask2d = np.ones((naxis2, naxis1), dtype=np.float32)
                        # apply useful region mask
                        image2d *= mask2d
                        # compute statistical analysis and update the image header
                        image2d_statsumm = statsumm(
                            image2d=image2d,
                            mask2d=mask2d,
                            header=output_header,
                            redustep=redustep,
                            rm_nan=True)
                        # compute run_astrometry: note that the function generates the output file
                        if 'maxfieldview_arcmin' in instconf['imagetypes'][redustep]:
                            maxfieldview_arcmin = instconf['imagetypes'][redustep]['maxfieldview_arcmin']
                        else:
                            msg = 'maxfieldview_arcmin missing in instrument configuration'
                            raise SystemError(msg)
                        # define possible P values for build-astrometry-index (scale number)
                        # in the order to be employed (if one fails, the next one is used)
                        # [see help of build-astrometry-index for details]; in addition, convert
                        # RA and DEC to DD.ddddd +/- DD.ddddd when necessary
                        if instrument == 'cafos':
                            pvalues = [2, 3, 1, 0, 4, 5, 6]
                        elif instrument == 'lsss':
                            pvalues = [6, 7, 8, 5, 4, 3, 2, 9]
                            ra_initial = output_header['ra']
                            ra_h, ra_m, ra_s = ra_initial.split()
                            ra_final = (float(ra_h) + float(ra_m)/60.0 + float(ra_s)/3600.0) * 15
                            output_header['ra'] = ra_final
                            dec_initial = output_header['dec']
                            dec_sign = dec_initial[0]
                            dec_d, dec_m, dec_s = dec_initial[1:].split()
                            dec_final = (float(dec_d) + float(dec_m)/60.0 + float(dec_s)/3600.0)
                            if dec_sign == '-':
                                dec_final = -dec_final
                            output_header['dec'] = dec_final
                        else:
                            msg = 'ERROR: instrument not included here!'
                            raise SystemError(msg)
                        ierr_astr, astrsumm1, astrsumm2 = run_astrometry(
                            image2d=image2d, mask2d=mask2d, saturpix=image2d_saturpix,
                            header=output_header,
                            maxfieldview_arcmin=maxfieldview_arcmin, fieldfactor=1.1, pvalues=pvalues,
                            nightdir=nightdir, output_fname=output_fname,
                            interactive=interactive, logfile=logfile, debug=False
                        )
                    # ---------------------------------------------------------
                    else:
                        msg = '* ERROR: combination of {} not implemented yet'.format(redustep)
                        raise SystemError(msg)

                    # update database with result using the mean MJD-OBS of
                    # the combined images as index
                    database[redustep][fname] = dict()
                    database[redustep][fname]['night'] = night
                    database[redustep][fname]['signature'] = imgsignature
                    database[redustep][fname]['fname'] = output_fname
                    database[redustep][fname]['statsumm'] = image2d_statsumm
                    dumdict = dict()
                    for keyword in instconf['masterkeywords']:
                        dumdict[keyword] = output_header[keyword]
                    database[redustep][fname]['masterkeywords'] = dumdict
                    database[redustep][fname]['ierr_bias'] = ierr_bias
                    database[redustep][fname]['delta_mjd_bias'] = delta_mjd_bias
                    database[redustep][fname]['bias_fname'] = bias_fname
                    database[redustep][fname]['ierr_flat'] = ierr_flat
                    database[redustep][fname]['delta_mjd_flat'] = delta_mjd_flat
                    database[redustep][fname]['flat_fname'] = flat_fname
                    database[redustep][fname]['ierr_astr'] = ierr_astr
                    if astrsumm1 is not None:
                        database[redustep][fname]['astr1_pixscale'] = astrsumm1.pixscale
                        database[redustep][fname]['astr1_ntargets'] = astrsumm1.ntargets
                        database[redustep][fname]['astr1_meanerr'] = astrsumm1.meanerr
                    if astrsumm2 is not None:
                        database[redustep][fname]['astr2_pixscale'] = astrsumm2.pixscale
                        database[redustep][fname]['astr2_ntargets'] = astrsumm2.ntargets
                        database[redustep][fname]['astr2_meanerr'] = astrsumm2.meanerr

                # update results database
                with open(databasefile, 'w') as outfile:
                    json.dump(database, outfile, indent=2)

                datetime_end = datetime.datetime.now()
                logfile.print('-> Reduction ends at.......: {}'.format(datetime_end), f=True)
                logfile.print('-> Elapsed time............: {}'.format(datetime_end - datetime_ini), f=True)

                # close and store log file with basic reduction
                logfile.print('Saving {}'.format(logfile.fname))
                logfile.close()
                if execute_reduction:
                    basename = os.path.basename(output_fname)
                    backupsubdir = basename[:-5]
                    backupsubdirfull = '{}/{}'.format(nightdir, backupsubdir)
                    if os.path.isdir(backupsubdirfull):
                        command = 'cp {} {}/'.format(logfile.fname, backupsubdirfull)
                        cmd = CmdExecute()
                        cmd.run(command)
                    else:
                        msg = 'ERROR: espected subdir {} not found'.format(backupsubdirfull)
                        raise SystemError(msg)

                if interactive:
                    ckey = input("Press 'x' + <ENTER> to stop, or simply <ENTER> to continue... ")
                    if ckey.lower() == 'x':
                        raise SystemExit()

        else:
            # skipping night (no images of sought type found)
            print('No {} images found. Skipping night!'.format(redustep))
