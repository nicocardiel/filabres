from astropy.io import fits
import datetime
import glob
import json
import numpy as np
import os
import sys
import uuid
import warnings

from .version import version

from filabres import LISTDIR
from filabres import REQ_OPERATORS


def classify_image(instconf, header):
    """
    Classify image in one of the expected types.

    The classification also checks that the specific requirements set
    to each image type are also met.
    Note that the function returns the first image type match without
    checking for additional potential matches.

    Parameters
    ----------
    instconf : dict
        Instrument configuration. See file configuration.yaml
        for details.
    header: astropy `Header` object

    Returns
    -------
    imagetype : str or None
        One of the expected image types (or None if the any of the
        requirements is not met).
    """

    imagetype = None

    for img in instconf['imagetypes']:
        requirements = instconf['imagetypes'][img]['requirements']
        typefound = True
        for keyword in requirements:
            operatorfound = False
            for operator in REQ_OPERATORS:
                lenop = len(operator)
                if keyword[-lenop:] == operator:
                    operatorfound = True
                    command = 'header[keyword[:-lenop]] ' + \
                              REQ_OPERATORS[operator] + \
                              ' requirements[keyword]'
                    if not eval(command):
                        typefound = False
                    break
            if not operatorfound:
                if requirements[keyword] != header[keyword]:
                    typefound = False
            if not typefound:
                break
        if typefound:
            imagetype = img
            break

    return imagetype


def initialize_auxdb(datadir, list_of_nights, instconf, verbose=False):
    """
    Generate database with relevant keywords for each night.

    Parameters
    ----------
    datadir : str
        Data directory containing the different nights to be reduced.
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    verbose : bool
        If True, display intermediate information.
    """

    # check for ./lists subdirectory
    if os.path.isdir(LISTDIR):
        if verbose:
            print('Subdirectory {} found'.format(LISTDIR))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(LISTDIR))
        os.makedirs(LISTDIR)

    probquantiles = instconf['probquantiles']
    # create one subdirectory for each night
    for night in list_of_nights:
        # subdirectory for current night
        nightdir = LISTDIR + night
        if os.path.isdir(nightdir):
            if verbose:
                print('Subdirectory {} found'.format(nightdir))
        else:
            if verbose:
                print('Subdirectory {} not found. '
                      'Creating it!'.format(nightdir))
            os.makedirs(nightdir)

        # get list of FITS files for current night
        filenames = datadir + night + '/*.fits'
        list_of_fits = glob.glob(filenames)
        list_of_fits.sort()

        # generate database for all the files in current night
        basefilename = nightdir + '/imagedb_' + instconf['instname']
        jsonfilename = basefilename + '.json'
        logfilename = basefilename + '.log'
        logfile = None
        imagedb = {
            'metainfo': {
                'instrument': instconf['instname'],
                'datadir': datadir,
                'night': night,
                'self': {
                    'creation_date': datetime.datetime.utcnow().isoformat(),
                    'thisfile': os.getcwd() + jsonfilename[1:],
                    'origin': sys.argv[0] + ', v.' + version,
                    'uuid': str(uuid.uuid1()),
                },
                'instconf': instconf
            }
        }

        # initalize lists with classified images
        for imagetype in instconf['imagetypes']:
            imagedb[imagetype] = dict()
        imagedb['unknown'] = dict()
        imagedb['saturated'] = dict()
        imagedb['wrong-instrument'] = dict()

        # get relevant keywords for each FITS file and classify it
        for filename in list_of_fits:
            # get image header
            basename = os.path.basename(filename)
            warningsfound = False
            # initially convert warnings into errors
            warnings.filterwarnings('error')
            try:
                with fits.open(filename) as hdul:
                    header = hdul[0].header
                    data = hdul[0].data
            except (UserWarning, ResourceWarning) as e:
                if logfile is None:
                    logfile = open(logfilename, 'wt')
                    print('* Creating {}'.format(logfilename))
                logfile.write('{} while reading {}\n'.format(
                              type(e).__name__, basename))
                logfile.write('{}\n'.format(e))
                print('{} while reading {}'.format(
                    type(e).__name__, basename))
                print(str(e))
                warningsfound = True
                # ignore warnings from here to avoid the messages:
                # Exception ignored in:...
                # ResourceWarning: unclosed file...
                warnings.filterwarnings('ignore')
            if warningsfound:
                # ignore warnings
                with fits.open(filename) as hdul:
                    header = hdul[0].header
            # check general instrument requirements
            requirements = instconf['requirements']
            fileok = True
            for keyword in requirements:
                if requirements[keyword] != header[keyword]:
                    fileok = False
            dumdict = dict()
            if fileok:
                # get master keywords for the current file
                for keyword in instconf['masterkeywords']:
                    if keyword in header:
                        dumdict[keyword] = header[keyword]
                    else:
                        print('ERROR: keyword {} is missing in '
                              'file {}'.format(keyword, basename))
                        raise SystemExit()
                # basic image statistics
                quantiles = np.quantile(data, probquantiles)
                for i, prob in enumerate(probquantiles):
                    keyword = 'QUAN{:04d}'.format(int(prob * 10000))
                    dumdict[keyword] = quantiles[i]
                # classify image
                imagetype = classify_image(instconf, header)
                if imagetype is None:
                    imagetype = 'unknown'
            else:
                imagetype = 'wrong-instrument'
            # include image in corresponding classification
            if imagetype in imagedb:
                imagedb[imagetype][basename] = dumdict
            else:
                print('ERROR: unexpected image type {} in'
                      'file {}'.format(imagetype, basename))
                raise SystemExit()

        # close logfile (if opened)
        if logfile is not None:
            logfile.close()

        # update number of images
        imagedb['metainfo']['num_allimages'] = len(list_of_fits)
        num_doublecheck = 0
        for imagetype in imagedb:
            if imagetype != 'metainfo':
                label = 'num_' + imagetype
                num = len(imagedb[imagetype])
                imagedb['metainfo'][label] = num
                num_doublecheck += num

        imagedb['metainfo']['num_doublecheck'] = num_doublecheck

        # generate JSON output file
        if verbose:
            print('* Creating {}'.format(jsonfilename))
        with open(jsonfilename, 'w') as outfile:
            json.dump(imagedb, outfile, indent=2)

        # double check
        if num_doublecheck != len(list_of_fits):
            print('ERROR: double check in number of files failed!')
            print('--> see file {}'.format(jsonfilename))
            raise SystemExit()
