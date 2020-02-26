from astropy.io import fits
import datetime
import json
import numpy as np
import os
import sys

from .astrometry import astrometry
from .maskfromflat import maskfromflat
from .retrieve_calibration import retrieve_calibration
from .signature import getkey_from_signature
from .statsumm import statsumm
from .version import version

from filabres import LISTDIR
SATURATION_LEVEL = 65000


def run_reduction_step(redustep, interactive, datadir, list_of_nights,
                       instconf, verbose=False, debug=False):
    """
    Execute reduction step.

    Parameters
    ==========
    redustep : str
        Reduction step to be executed.
    interactive : bool
        If True, enable interactive execution (e.g. plots,...).
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
            for filename in list_of_images:
                # signature of particular image
                imgsignature = dict()
                for keyword in signaturekeys:
                    imgsignature[keyword] = imagedb[redustep][filename][keyword]

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

                # define output FITS file using the file name of the first
                # image in the block (appending the _red suffix)
                output_filename = nightdir + '/' + redustep + '_'
                output_filename += filename[:-5] + '_red.fits'
                if verbose:
                    print('-> output filename will be {}'.format(output_filename))

                # declare temporary cube to store the images to be combined
                naxis1 = getkey_from_signature(imgsignature, 'NAXIS1')
                naxis2 = getkey_from_signature(imgsignature, 'NAXIS2')
                image2d_saturpix = np.zeros((naxis2, naxis1), dtype=np.bool)

                with fits.open(datadir + night + '/' + filename) as hdulist:
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
                    val1 = output_header[keyword]
                    val2 = imagedb[redustep][filename][keyword]
                    if val1 != val2:
                        output_header[keyword] = val2
                        print('WARNING: {} changed from {} to {}'.format(keyword, val1, val2))
                output_header.add_history('Creating {} file:'.format(redustep))
                saturpix = np.where(image2d >= SATURATION_LEVEL)
                image2d_saturpix[saturpix] = True
                output_header.add_history(os.path.basename(filename))
                output_header.add_history('Signature:')
                for key in imgsignature:
                    output_header.add_history(' - {}: {}'.format(key, imgsignature[key]))

                # combine images according to their type
                # ---------------------------------------------------------
                if redustep == 'science-imaging':
                    mjdobs = output_header['MJD-OBS']
                    # retrieve and subtract bias
                    ierr_bias, image2d_bias, bias_filename = retrieve_calibration(
                            instrument, 'bias', imgsignature, mjdobs,
                            verbose=verbose
                        )
                    output_header.add_history('Subtracting bias:')
                    output_header.add_history(bias_filename)
                    if debug:
                        print('bias level:', np.median(image2d_bias))
                    image2d -= image2d_bias
                    # retrieve and divide by flatfield
                    ierr_flat, image2d_flat, flat_filename = retrieve_calibration(
                            instrument, 'flat-imaging', imgsignature,
                            mjdobs, verbose=verbose
                        )
                    output_header.add_history('Applying flatfield:')
                    output_header.add_history(flat_filename)
                    if debug:
                        print('flat level:', np.median(image2d_flat))
                    image2d /= image2d_flat
                    # generate useful region mask from flatfield
                    mask2d = maskfromflat(image2d_flat)
                    if debug:
                        print('masked pixels: {}/{}'.format(np.sum(mask2d == 0.0), naxis1 * naxis2))
                    # apply useful region mask
                    image2d *= mask2d
                    # compute statistical analysis and update the image header
                    image2d_statsum = statsumm(image2d, output_header, redustep, rm_nan=True)
                    # compute astrometry: note that the function generates the output file
                    if 'maxfieldview_arcmin' in instconf['imagetypes'][redustep]:
                        maxfieldview_arcmin = instconf['imagetypes'][redustep]['maxfieldview_arcmin']
                    else:
                        msg = 'maxfieldview_arcmin missing in instrument configuration'
                        raise SystemError(msg)
                    astrometry(image2d=image2d, mask2d=mask2d, saturpix=image2d_saturpix,
                               header=output_header,
                               maxfieldview_arcmin=maxfieldview_arcmin, fieldfactor=1.1,
                               nightdir=nightdir, output_filename=output_filename,
                               interactive=interactive, verbose=verbose, debug=False)
                # ---------------------------------------------------------
                else:
                    msg = '* ERROR: combination of {} not implemented yet'.format(redustep)
                    raise SystemError(msg)

                # update database with result using the mean MJD-OBS of
                # the combined images as index
                database[redustep][filename] = dict()
                database[redustep][filename]['night'] = night
                database[redustep][filename]['signature'] = imgsignature
                database[redustep][filename]['filename'] = output_filename
                database[redustep][filename]['statsumm'] = image2d_statsum
                dumdict = dict()
                for keyword in instconf['masterkeywords']:
                    dumdict[keyword] = output_header[keyword]
                database[redustep][filename]['masterkeywords'] = dumdict
                if ierr_bias is not None:
                    database[redustep][filename]['ierr_bias'] = ierr_bias
                if ierr_flat is not None:
                    database[redustep][filename]['ierr_flat'] = ierr_flat

            # update results database
            with open(databasefile, 'w') as outfile:
                json.dump(database, outfile, indent=2)

        else:
            # skipping night (no images of sought type found)
            if verbose:
                print('No {} images found. Skipping night!'.format(redustep))
