import glob
import json
import os

from filabres import LISTDIR


def list_classified(imagetype, args_night):
    """
    Display list with already classified images of the selected type

    Parameters
    ==========
    imagetype : str
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
    args_night : str or None
        Selected night

    """

    # check for ./lists subdirectory
    if not os.path.isdir(LISTDIR):
        msg = "Subdirectory {} not found"
        raise SystemError(msg)

    if args_night is None:
        night = '*'
    else:
        night = args_night

    list_of_imagedb = glob.glob(LISTDIR + night + '/imagedb_*.json')
    list_of_imagedb.sort()

    for jsonfilename in list_of_imagedb:

        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except:
            raise SystemError('File {} not found'.format(jsonfilename))

        datadir = imagedb['metainfo']['datadir']
        night = imagedb['metainfo']['night']
        if imagetype in imagedb:
            for filename in imagedb[imagetype]:
                print(datadir + night + '/' + filename, end= ' ')

    print()
