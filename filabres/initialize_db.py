from astropy.io import fits
import datetime
import glob
import os
import uuid
import json


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

    for night in list_of_nights:
        # create one subdirectory for each night
        nightdir = subdir + night
        if os.path.isdir(nightdir):
            if verbose:
                print('Subdirectory {} found'.format(nightdir))
        else:
            if verbose:
                print('Subdirectory {} not found. '
                      'Creating it!'.format(nightdir))
            os.makedirs(nightdir)

        # generate database for all the files
        database = {'metainfo': dict(), 'images': dict()}
        database['metainfo'] = {
            'creation_date': datetime.datetime.utcnow().isoformat(),
            'uuid': str(uuid.uuid1()),
            'datadir': datadir,
            'instconf': instconf
        }
        filenames = datadir + night + '/*.fits'
        list_of_fits = glob.glob(filenames)
        for filename in list_of_fits:
            basename = os.path.basename(filename)
            with fits.open(filename) as hdul:
                header = hdul[0].header
            dumdict = dict()
            for keyword in instconf['keywords']:
                dumdict[keyword] = header[keyword]
            database['images'][basename] = dumdict

        jsonfilename = nightdir + '/allfiles.json'
        if verbose:
            print('* Creating {}'.format(jsonfilename))
        with open(jsonfilename, 'w') as outfile:
            json.dump(database, outfile, indent=2)
