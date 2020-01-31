from astropy.io import fits
import datetime
import glob
import json
import os
import sys
import uuid

from .version import version

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


def initialize_db(datadir, list_of_nights, instconf, verbose=False):
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
    subdir = './lists/'
    if os.path.isdir(subdir):
        if verbose:
            print('Subdirectory {} found'.format(subdir))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(subdir))
        os.makedirs(subdir)

    # create one subdirectory for each night
    for night in list_of_nights:
        # subdirectory for current night
        nightdir = subdir + night
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
        jsonfilename = nightdir + '/imagedb_' + instconf['instname'] + '.json'
        database = {
            'metainfo': {
                'creation_date': datetime.datetime.utcnow().isoformat(),
                'self': os.getcwd() + jsonfilename[1:],
                'origin': sys.argv[0] + ', v.' + version,
                'uuid': str(uuid.uuid1()),
                'datadir': datadir,
                'instconf': instconf
            },
            'allimages': dict(),
            'lists': dict()
        }

        # initalize lists with classified images
        for imagetype in instconf['imagetypes']:
            database['lists'][imagetype] = []
        database['lists']['unknown'] = []
        database['lists']['wrong-instrument'] = []

        # get relevant keywords for each FITS file and classify it
        for filename in list_of_fits:
            # get image header
            basename = os.path.basename(filename)
            with fits.open(filename) as hdul:
                header = hdul[0].header
            # check general instrument requirements
            requirements = instconf['requirements']
            fileok = True
            for key in requirements:
                if requirements[key] != header[key]:
                    fileok = False
            if fileok:
                # get master keywords for the current file
                dumdict = dict()
                for keyword in instconf['masterkeywords']:
                    if keyword in header:
                        dumdict[keyword] = header[keyword]
                    else:
                        print('ERROR: keyword {} is missing in '
                              'file {}'.format(keyword, basename))
                        raise SystemExit()
                database['allimages'][basename] = dumdict
                # classify image
                imagetype = classify_image(instconf, header)
                if imagetype is None:
                    imagetype = 'unknown'
            else:
                imagetype = 'wrong-instrument'
            # include image in corresponding classification
            if imagetype in database['lists']:
                database['lists'][imagetype].append(basename)
            else:
                print('ERROR: unexpected image type {} in'
                      'file {}'.format(imagetype, basename))
                raise SystemExit()

        # update number of images
        database['metainfo']['num_allimages'] = len(list_of_fits)
        num_doublecheck = 0
        for imagetype in database['lists']:
            label = 'num_' + imagetype
            num = len(database['lists'][imagetype])
            database['metainfo'][label] = num
            num_doublecheck += num

        database['metainfo']['num_doublecheck'] = num_doublecheck

        # generate JSON output file
        if verbose:
            print('* Creating {}'.format(jsonfilename))
        with open(jsonfilename, 'w') as outfile:
            json.dump(database, outfile, indent=2)

        # double check
        if num_doublecheck != len(list_of_fits):
            print('ERROR: double check in number of files failed!')
            print('--> see file {}'.format(jsonfilename))
            raise SystemExit()
