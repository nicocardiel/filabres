from astropy.io import fits
from astropy.time import Time
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


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def run_reduction_step(args_database, redustep, datadir, list_of_nights,
                       instconf, verbose=False, debug=False):
    """
    Execute reduction step.

    Parameters
    ==========
    args_database : str or None
        Main database file name.
    redustep : str
        Reduction step to be executed.
    datadir : str
        Data directory containing the different nights to be reduced.
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

    # main database
    if args_database is None:
        databasefile = 'filabres_db.json'
    else:
        databasefile = args_database
    try:
        with open(databasefile) as jfile:
            database = json.load(jfile)
    except FileNotFoundError:
        database = {}
    if verbose:
        print('* Main database set to {}'.format(databasefile))

    # check for subdirectory
    if os.path.isdir(redustep):
        if verbose:
            print('Subdirectory {} found'.format(redustep))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(redustep))
        os.makedirs(redustep)

    # prepare main database
    if redustep not in database:
        database[redustep] = dict()

    # set maxtimespan_hours
    maxtimespan_hours = instconf['imagetypes'][redustep]['maxtimespan_hours']

    # loop in night
    for night in list_of_nights:

        # read local image database for current night
        jsonfilename = LISTDIR + night + '/imagedb_' + \
                       instconf['instname'] + '.json'
        if verbose:
            print('* Reading file {}'.format(jsonfilename))
        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            print('ERROR: file {} not found'.format(jsonfilename))
            print('Try using -rs initialize')
            raise SystemExit()

        # check version of instrument configuration
        if instconf['version'] != imagedb['metainfo']['instconf']['version']:
            print('ERROR: different versions of instrument configuration')
            raise SystemExit()

        # select images of the requested type
        list_of_images = list(imagedb[redustep].keys())
        nlist_of_images = len(list_of_images)
        if verbose:
            print('* Number of {} images found {}'.format(
                redustep, nlist_of_images))

        if nlist_of_images > 0:

            # create subdirectory to store results for current night
            nightdir = redustep + '/' + night
            if os.path.isdir(nightdir):
                if verbose:
                    print('Subdirectory {} found'.format(nightdir))
            else:
                if verbose:
                    print('Subdirectory {} not found. '
                          'Creating it!'.format(nightdir))
                os.makedirs(nightdir)

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
                print('* Number of different signatures found:', nsignatures)

            # select images with a common signature and subdivide this
            # selection into blocks where the images are grouped within
            # the indicated time span
            for isignature in range(len(list_of_signatures)):
                signature = list_of_signatures[isignature]
                images_with_fixed_signature = []
                for filename in list_of_images:
                    # signature of particular image
                    imgsignature = dict()
                    for keyword in signaturekeys:
                        imgsignature[keyword] = \
                            imagedb[redustep][filename][keyword]
                    if imgsignature == signature:
                        images_with_fixed_signature.append(
                            datadir + night + '/' + filename)
                nfiles = len(images_with_fixed_signature)
                if nfiles == 0:
                    msg = '* ERROR: unexpected number of {} images = 0'.format(
                          nfiles)
                    raise SystemError(msg)
                # dictionary indicating if the images with this signature
                # have been classified
                classified_images = dict()
                for filename in images_with_fixed_signature:
                    classified_images[filename] = False
                if verbose:
                    print('- signature:')
                    for key in signature:
                        print(key, signature[key])
                    print('- Total number of images with this signature:',
                          len(images_with_fixed_signature))
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
                        for key in classified_images:
                            if not classified_images[key]:
                                basename = os.path.basename(key)
                                t = imagedb[redustep][basename]['MJD-OBS']
                                mean_mjdobs += t
                                imgblock.append(key)
                                break
                    else:
                        t0 = None
                        for key in classified_images:
                            if not classified_images[key]:
                                basename = os.path.basename(key)
                                t = imagedb[redustep][basename]['MJD-OBS']
                                if len(imgblock) == 0:
                                    imgblock.append(key)
                                    t0 = imagedb[redustep][basename]['MJD-OBS']
                                    mean_mjdobs += t0
                                else:
                                    if abs(t-t0) < maxtimespan_hours/24:
                                        imgblock.append(key)
                                        mean_mjdobs += t
                    imgblock.sort()
                    print(imgblock)
                    nfiles = len(imgblock)
                    originf = [os.path.basename(dum) for dum in imgblock]
                    mean_mjdobs /= nfiles
                    if verbose:
                        print('- Number of images with expected signature and '
                              'within time span:', nfiles)
                        if debug:
                            for filename in imgblock:
                                print(filename)

                    # declare temporary cube to store the images to be combined
                    naxis1 = getkey_from_signature(signature, 'NAXIS1')
                    naxis2 = getkey_from_signature(signature, 'NAXIS2')
                    image3d = np.zeros((nfiles, naxis2, naxis1),
                                       dtype=np.float32)

                    # output file name
                    output_header = None

                    # store images in temporary data cube
                    for i in range(nfiles):
                        filename = imgblock[i]
                        with fits.open(filename) as hdulist:
                            image_header = hdulist[0].header
                            image_data = hdulist[0].data
                        if i == 0:
                            output_header = image_header
                            output_header.add_history("---")
                            output_header.add_history(
                                'Using filabres v.{}'.format(version))
                            output_header.add_history(
                                'Date: ' + str(
                                    datetime.datetime.utcnow().isoformat())
                            )
                            output_header.add_history(sys.argv)
                            # avoid warning when saving FITS
                            if output_header['BLANK']:
                                del output_header['BLANK']
                            # check MJD-OBS is not negative
                            mjdobs = output_header['MJD-OBS']
                            if mjdobs < 0:
                                tinit = Time(output_header['DATE-OBS'],
                                             format='isot', scale='utc')
                                output_header['MJD-OBS'] = tinit.mjd
                                output_header.add_history(
                                    'MJD-OBS changed from {} to {:.5f}'.format(
                                        mjdobs, tinit.mjd
                                    )
                                )
                                print('* WARNING: MJD-OBS change from {} to '
                                      '{:.5f}'.format(mjdobs, tinit.mjd))
                            output_header.add_history(
                                'Using {} images to compute {}:'.format(
                                    nfiles, redustep))
                        image3d[i, :, :] += image_data
                        output_header.add_history(
                            os.path.basename(filename))
                    output_header.add_history('Signature:')
                    for key in signature:
                        output_header.add_history(
                            ' - {}: {}'.format(key, signature[key])
                        )

                    # combine images according to their type
                    if redustep == 'bias':
                        # median combination
                        image2d = np.median(image3d, axis=0)
                        output_header.add_history(
                            'Combination method: median'
                        )
                    elif redustep == 'flat-imaging':
                        # retrieve and subtract bias
                        mjdobs = output_header['MJD-OBS']
                        image2d_bias = retrieve_calibration(
                            'bias', signature, mjdobs, database,
                            verbose=verbose
                        )
                        if debug:
                            print('bias level:', np.median(image2d_bias))
                        for i in range(nfiles):
                            # subtract bias
                            image3d[i, :, :] -= image2d_bias
                            # normalize by the median value
                            image3d[i, :, :] /= np.median(image3d[i, :, :])
                        # median combination of normalized images
                        image2d = np.median(image3d, axis=0)
                        # set to 1.0 pixels with values <= 0
                        image2d[image2d <= 0.0] = 1.0
                        output_header.add_history(
                            'Combination method: median of normalized images'
                        )
                    else:
                        msg = '* ERROR: combination of {} not implemented' + \
                              ' yet'.format(redustep)
                        raise SystemError(msg)

                    # generate string with signature values
                    sortedkeys, ssig = signature_string(signature)
                    if 'sortedkeys' not in database[redustep]:
                        database[redustep]['sortedkeys'] = sortedkeys
                    else:
                        if sortedkeys != database[redustep]['sortedkeys']:
                            print('* ERROR: sortedkeys have changed when'
                                  'reducing {} images'.format(redustep))
                            raise SystemExit()

                    # note: the following step must be performed before
                    # saving the combined image; otherwise, the cleanup
                    # procedure will delete the just created combined image
                    if ssig not in database[redustep]:
                        # update main database with new signature if not present
                        database[redustep][ssig] = dict()
                    else:
                        # check that there is not a combined image using any
                        # of the individual images of imgblock: otherwise, some
                        # entries of the main database must be removed and the
                        # associated reduced images deleted
                        if len(database[redustep][ssig]) > 0:
                            mjdobs_to_be_deleted = []
                            for mjdobs in database[redustep][ssig]:
                                old_originf = \
                                    database[redustep][ssig][mjdobs]['originf']
                                # is there intersection?
                                conflict = list(set(originf) & set(old_originf))
                                if len(conflict) > 0:
                                    mjdobs_to_be_deleted.append(mjdobs)
                                    print('WARNING: deleting previous database'
                                          ' entry')
                                    filename = database[redustep][ssig][mjdobs][
                                        'filename']
                                    print('Deleting {}'.format(filename))
                                    if os.path.exists(filename):
                                        os.remove(filename)
                            for mjdobs in mjdobs_to_be_deleted:
                                del database[redustep][ssig][mjdobs]

                    # statistical analysis
                    image2d_statsum = statsumm(image2d, rm_nan=True)
                    output_header.add_history('Statistical analysis of combined'
                                              ' {} image:'.format(redustep))
                    for key in image2d_statsum:
                        output_header.add_history(' - {}: {}'.format(
                            key, image2d_statsum[key]
                        ))

                    # save output FITS file using the file name of the first
                    # image in the block (appending the _red suffix)
                    output_filename = nightdir + '/' + redustep
                    dumfile = os.path.basename(imgblock[0])
                    output_filename += dumfile[:-5] + '_red.fits'
                    print('-> output filename {}'.format(output_filename))

                    hdu = fits.PrimaryHDU(image2d.astype(np.float32),
                                          output_header)
                    hdu.writeto(output_filename, overwrite=True)

                    # update database with result using the mean MJD-OBS of the
                    # combined images as index
                    mjdobs = '{:.5f}'.format(mean_mjdobs)
                    database[redustep][ssig][mjdobs] = dict()
                    database[redustep][ssig][mjdobs]['filename'] = \
                        output_filename
                    database[redustep][ssig][mjdobs]['statsumm'] = \
                        image2d_statsum
                    database[redustep][ssig][mjdobs]['norigin'] = nfiles
                    database[redustep][ssig][mjdobs]['originf'] = originf

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
                print('- No {} images found. Skipping night!'.format(redustep))

    # update main database
    with open(databasefile, 'w') as outfile:
        json.dump(database, outfile, indent=2)
