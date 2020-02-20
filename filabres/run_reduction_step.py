from astropy.io import fits
import datetime
import json
import numpy as np
import os
import sys

from .retrieve_calibration import retrieve_calibration
from .signature import getkey_from_signature
from .signature import signature_string
from .statsumm import statsumm
from .version import version

from filabres import LISTDIR


def run_reduction_step(redustep, datadir, list_of_nights,
                       instconf, verbose=False, debug=False):
    """
    Execute reduction step.

    Parameters
    ==========
    redustep : str
        Reduction step to be executed.
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    verbose : bool
        If True, display intermediate information.
    debug : bool
        Display additional debugging information.
    """

    instrument = instconf['instname']

    # classification of the reduction step
    classification = instconf['imagetypes'][redustep]['classification']

    if classification == 'calibration':
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
    else:
        # in this case the database will be stored in separate files (one
        # for each night)
        databasefile = None
        database = None

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

    # loop in night
    for inight, night in enumerate(list_of_nights):

        print('\n* Working with night {} ({}/{})'.format(night, inight + 1, len(list_of_nights)))

        # read local image database for current night
        jsonfilename = LISTDIR + night + '/imagedb_'
        jsonfilename += instconf['instname'] + '.json'
        if verbose:
            print('Reading file {}'.format(jsonfilename))
        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            print('ERROR: file {} not found'.format(jsonfilename))
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

            if classification != 'calibration':
                # set the expected database: note that for science images, this
                # database is stored as an independent JSON file for each night
                databasefile = nightdir + '/'
                databasefile += 'filabres_db_{}_{}.json'.format(instrument, redustep)
                try:
                    with open(databasefile) as jfile:
                        database = json.load(jfile)
                except FileNotFoundError:
                    database = {}
                if verbose:
                    print('\nResults database set to {}'.format(databasefile))

            # determine number of different signatures
            signaturekeys = instconf['imagetypes'][redustep]['signature']
            list_of_signatures = []
            for filename in list_of_images:
                # signature of particular image
                imgsignature = dict()
                for keyword in signaturekeys:
                    imgsignature[keyword] = imagedb[redustep][filename][keyword]
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
                for filename in list_of_images:
                    # signature of particular image
                    imgsignature = dict()
                    for keyword in signaturekeys:
                        imgsignature[keyword] = imagedb[redustep][filename][keyword]
                    if imgsignature == signature:
                        images_with_fixed_signature.append(datadir + night + '/' + filename)
                images_with_fixed_signature.sort()
                nfiles = len(images_with_fixed_signature)
                if nfiles == 0:
                    msg = 'ERROR: unexpected number of {} images = 0'.format(nfiles)
                    raise SystemError(msg)
                # dictionary indicating if the images with this signature
                # have been classified
                classified_images = dict()
                for filename in images_with_fixed_signature:
                    classified_images[filename] = False
                if verbose:
                    print('Signature ({}/{}):'.format(isignature+1, len(list_of_signatures)))
                    for key in signature:
                        print(' - {}: {}'.format(key, signature[key]))
                    print('Total number of images with this signature:', len(images_with_fixed_signature))
                    if debug:
                        for filename in images_with_fixed_signature:
                            print(filename, end=' ')
                        print()

                images_pending = True
                while images_pending:

                    # select images with the same signature and within the
                    # specified maximum time span
                    imgblock = []
                    mean_mjdobs = 0.0
                    if maxtimespan_hours == 0:
                        # reduce individual images
                        for filename in classified_images:
                            if not classified_images[filename]:
                                basename = os.path.basename(filename)
                                if verbose:
                                    print(' - {}'.format(filename))
                                t = imagedb[redustep][basename]['MJD-OBS']
                                mean_mjdobs += t
                                imgblock.append(filename)
                                break
                    else:
                        t0 = None
                        for filename in classified_images:
                            if not classified_images[filename]:
                                basename = os.path.basename(filename)
                                t = imagedb[redustep][basename]['MJD-OBS']
                                if len(imgblock) == 0:
                                    imgblock.append(filename)
                                    t0 = imagedb[redustep][basename]['MJD-OBS']
                                    mean_mjdobs += t0
                                else:
                                    if abs(t-t0) < maxtimespan_hours/24:
                                        if verbose:
                                            print(' - {}'.format(filename))
                                        imgblock.append(filename)
                                        mean_mjdobs += t
                    imgblock.sort()
                    nfiles = len(imgblock)
                    originf = [os.path.basename(dum) for dum in imgblock]
                    mean_mjdobs /= nfiles
                    if verbose:
                        print('> Number of images with expected signature and within time span:', nfiles)
                        if debug:
                            for filename in imgblock:
                                print(filename)

                    # declare temporary cube to store the images to be combined
                    naxis1 = getkey_from_signature(signature, 'NAXIS1')
                    naxis2 = getkey_from_signature(signature, 'NAXIS2')
                    image3d = np.zeros((nfiles, naxis2, naxis1), dtype=np.float32)
                    exptime = np.zeros(nfiles, dtype=np.float32)

                    # output file name
                    output_header = None

                    # store images in temporary data cube
                    for i in range(nfiles):
                        filename = imgblock[i]
                        basename = os.path.basename(filename)
                        exptime[i] = imagedb[redustep][basename]['EXPTIME']
                        with fits.open(filename) as hdulist:
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
                                val1 = output_header[keyword]
                                val2 = imagedb[redustep][basename][keyword]
                                if val1 != val2:
                                    output_header[keyword] = val2
                                    print('WARNING: {} changed from {} to {}'.format(keyword, val1, val2))
                            output_header.add_history('Using {} images to compute {}:'.format(nfiles, redustep))
                        image3d[i, :, :] += image_data
                        output_header.add_history(os.path.basename(filename))
                    output_header.add_history('Signature:')
                    for key in signature:
                        output_header.add_history(' - {}: {}'.format(key, signature[key]))

                    # combine images according to their type
                    ierr_bias = None
                    ierr_flat = None
                    if redustep == 'bias':
                        # median combination
                        image2d = np.median(image3d, axis=0)
                        output_header.add_history('Combination method: median')
                    elif redustep == 'flat-imaging':
                        mjdobs = output_header['MJD-OBS']
                        # retrieve and subtract bias
                        ierr_bias, image2d_bias, bias_filename = retrieve_calibration(
                                instrument, 'bias', signature, mjdobs,
                                verbose=verbose
                            )
                        output_header.add_history('Subtracting bias:')
                        output_header.add_history(bias_filename)
                        if debug:
                            print('bias level:', np.median(image2d_bias))
                        for i in range(nfiles):
                            # subtract bias
                            image3d[i, :, :] -= image2d_bias
                            # normalize by the median value
                            mediansignal = np.median(image3d[i, :, :])
                            if mediansignal > 0:
                                image3d[i, :, :] /= mediansignal
                        # median combination of normalized images
                        image2d = np.median(image3d, axis=0)
                        # set to 1.0 pixels with values <= 0
                        image2d[image2d <= 0.0] = 1.0
                        output_header.add_history('Combination method: median of normalized images')
                    elif redustep == 'science-imaging':
                        mjdobs = output_header['MJD-OBS']
                        # retrieve and subtract bias
                        ierr_bias, image2d_bias, bias_filename = retrieve_calibration(
                                instrument, 'bias', signature, mjdobs,
                                verbose=verbose
                            )
                        output_header.add_history('Subtracting bias:')
                        output_header.add_history(bias_filename)
                        if debug:
                            print('bias level:', np.median(image2d_bias))
                        for i in range(nfiles):
                            # subtract bias
                            image3d[i, :, :] -= image2d_bias
                        # retrieve and divide by flatfield
                        ierr_flat, image2d_flat, flat_filename = retrieve_calibration(
                                instrument, 'flat-imaging', signature,
                                mjdobs, verbose=verbose
                            )
                        output_header.add_history('Applying flatfield:')
                        output_header.add_history(flat_filename)
                        if debug:
                            print('flat level:', np.median(image2d_flat))
                        for i in range(nfiles):
                            image3d[i, :, :] /= image2d_flat
                        # rescale every single image to the exposure time
                        # of the first image
                        for i in range(nfiles):
                            if exptime[0] == exptime[i]:
                                factor = 1.0
                            else:
                                if exptime[i] <= 0:
                                    msg = 'Unexpected EXPTIME={}'.format(exptime[i])
                                    raise SystemError(msg)
                                factor = exptime[0]/exptime[i]
                            image3d[i, :, :] *= factor
                        # median combination of rescaled images
                        image2d = np.median(image3d, axis=0)
                    else:
                        msg = '* ERROR: combination of {} not implemented yet'.format(redustep)
                        raise SystemError(msg)

                    # generate string with signature values
                    sortedkeys, ssig = signature_string(signature)
                    if 'sortedkeys' not in database:
                        database['sortedkeys'] = sortedkeys
                    else:
                        if sortedkeys != database['sortedkeys']:
                            msg = 'ERROR: sortedkeys have changed when reducing {} images'.format(redustep)
                            raise SystemError(msg)

                    # note: the following step must be performed before
                    # saving the combined image; otherwise, the cleanup
                    # procedure will delete the just created combined image
                    if redustep not in database:
                        database[redustep] = dict()
                    if ssig not in database[redustep]:
                        # update main database with new signature
                        # if not present
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
                                    filename = database[redustep][ssig][mjdobs]['filename']
                                    if os.path.exists(filename):
                                        print('Deleting {}'.format(filename))
                                        os.remove(filename)
                            for mjdobs in mjdobs_to_be_deleted:
                                print('WARNING: deleting previous database entry: {} --> {} --> {}'.format(
                                        redustep, ssig, mjdobs
                                    )
                                )
                                del database[redustep][ssig][mjdobs]

                    # statistical analysis
                    image2d_statsum = statsumm(image2d, rm_nan=True)
                    output_header.add_history('Statistical analysis of combined {} image:'.format(redustep))
                    for key in image2d_statsum:
                        output_header.add_history(' - {}: {}'.format(key, image2d_statsum[key]))

                    # save output FITS file using the file name of the first
                    # image in the block (appending the _red suffix)
                    output_filename = nightdir + '/' + redustep + '_'
                    dumfile = os.path.basename(imgblock[0])
                    output_filename += dumfile[:-5] + '_red.fits'
                    print('-> output filename {}'.format(output_filename))

                    hdu = fits.PrimaryHDU(image2d.astype(np.float32), output_header)
                    hdu.writeto(output_filename, overwrite=True)

                    # update database with result using the mean MJD-OBS of
                    # the combined images as index
                    mjdobs = '{:.5f}'.format(mean_mjdobs)
                    database[redustep][ssig][mjdobs] = dict()
                    database[redustep][ssig][mjdobs]['night'] = night
                    database[redustep][ssig][mjdobs]['signature'] = signature
                    database[redustep][ssig][mjdobs]['filename'] = output_filename
                    database[redustep][ssig][mjdobs]['statsumm'] = image2d_statsum
                    dumdict = dict()
                    for keyword in instconf['masterkeywords']:
                        dumdict[keyword] = output_header[keyword]
                    database[redustep][ssig][mjdobs]['masterkeywords'] = dumdict
                    database[redustep][ssig][mjdobs]['norigin'] = nfiles
                    database[redustep][ssig][mjdobs]['originf'] = originf
                    if ierr_bias is not None:
                        database[redustep][ssig][mjdobs]['ierr_bias'] = ierr_bias
                    if ierr_flat is not None:
                        database[redustep][ssig][mjdobs]['ierr_flat'] = ierr_flat

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
            # update results database
            if classification != 'calibration':
                with open(databasefile, 'w') as outfile:
                    json.dump(database, outfile, indent=2)

        else:
            # skipping night (no images of sought type found)
            if verbose:
                print('No {} images found. Skipping night!'.format(redustep))

    # update results database
    if classification == 'calibration':
        with open(databasefile, 'w') as outfile:
            json.dump(database, outfile, indent=2)
