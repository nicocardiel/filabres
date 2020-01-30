from astropy.io import fits
import datetime
import glob
import json
import numpy as np
import os
import sys
import uuid

from .version import version


def initialize_db(datadir, list_of_nights, instconf, verbose=False):
    """Generate database with relevant keywords for each night.

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
            'allimages': dict()
        }
        imagetypes = instconf['imagetypes'].keys()

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
                    dumdict[keyword] = header[keyword]
                database['allimages'][basename] = dumdict
                # classify image
                imagetype = None
                for img in instconf['imagetypes']:
                    requirements = instconf['imagetypes'][img]['requirements']
                    typefound = True
                    for key in requirements:
                        if requirements[key] != header[key]:
                            typefound = False
                    if typefound:
                        imagetype = img
                if imagetype is None:
                    imagetype = 'unknown'

            else:
                imagetype = '.not.' + instconf['instname']
            # include image in corresponding classification
            if imagetype in database:
                database[imagetype].append(basename)
            else:
                database[imagetype] = [basename]

        # update number of images
        database['metainfo']['numtotal'] = len(list_of_fits)
        # ToDo: seguir aqui
        """
        for imagetyp in imagetypes:
            label = 'num' + imagetyp
            database['metainfo'][label] = len(database[imagetyp])
        """

        # generate JSON output file
        if verbose:
            print('* Creating {}'.format(jsonfilename))
        with open(jsonfilename, 'w') as outfile:
            json.dump(database, outfile, indent=2)
