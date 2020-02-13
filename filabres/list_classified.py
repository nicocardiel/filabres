import glob
import json
import os
import pandas as pd

from filabres import LISTDIR


def list_classified(img1, img2, args_night):
    """
    Display list with already classified images of the selected type

    Parameters
    ==========
    img1 : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
        The file names are listed in a single line, separated by a
        single blank space.
    img2 : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
        Each file name is displayed in a different line, together
        with the quantile information.
    args_night : str or None
        Selected night

    """

    if img1 is None:
        if img2 is None:
            return
        else:
            imagetype = img2
    else:
        if img2 is None:
            imagetype = img1
        else:
            print('ERROR: do not use -l and -ls simultaneously.')
            raise SystemExit()

    df = None  # Avoid PyCharm warning

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

    n = 0

    for jsonfilename in list_of_imagedb:

        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            raise SystemError('File {} not found'.format(jsonfilename))

        datadir = imagedb['metainfo']['datadir']
        night = imagedb['metainfo']['night']
        if imagetype in imagedb:
            for filename in imagedb[imagetype]:
                outfile = datadir + night + '/' + filename
                n += 1
                if img1 is not None:
                    print(datadir + night + '/' + filename, end=' ')
                else:
                    quantiles = imagedb[imagetype][filename]['quantiles']
                    if n == 1:
                        colnames = ['file'] + list(quantiles.keys())
                        df = pd.DataFrame(columns=colnames)
                    df.loc[n-1] = \
                        [os.path.basename(outfile)] + list(quantiles.values())

    if img1 is not None:
        if n > 0:
            print()
    else:
        if df is not None:
            if df.shape[0] > 0:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                print(df.round(1).to_string(index=False))

    raise SystemExit()
