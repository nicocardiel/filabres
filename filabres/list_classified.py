import glob
import json
import os
import pandas as pd

from filabres import DATADIR
from filabres import LISTDIR


def list_classified(img1, img2, args_night, args_keyword):
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
    args_keyword : list or None
        List with additional keywords to be displayed when img2
        is not None (otherwise an error is raised). Note that each
        value in this list is also a list (with a single keyword).

    """

    # protections
    if args_keyword is not None:
        if img2 is None:
            print('ERROR: -k KEYWORD is only valid together with -lq')
            raise SystemExit()
        else:
            lkeyword = [item[0].upper() for item in args_keyword]
    else:
        lkeyword = None

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
    colnames = None

    for jsonfilename in list_of_imagedb:

        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            raise SystemError('File {} not found'.format(jsonfilename))

        night = imagedb['metainfo']['night']
        if imagetype in imagedb:
            for filename in imagedb[imagetype]:
                outfile = DATADIR + night + '/' + filename
                n += 1
                if img1 is not None:
                    print(DATADIR + night + '/' + filename, end=' ')
                else:
                    quantiles = imagedb[imagetype][filename]['quantiles']
                    storedkeywords = imagedb[imagetype][filename]
                    colnames_ = ['file']
                    colnames_ += list(quantiles.keys())
                    if lkeyword is not None:
                        for keyword in lkeyword:
                            if keyword not in storedkeywords:
                                print('ERROR: keyword {} is not stored in '
                                      'the image database'.format(keyword))
                                raise SystemExit()
                            colnames_ += [keyword]
                    if n == 1:
                        colnames = colnames_
                        df = pd.DataFrame(columns=colnames)
                    else:
                        if colnames_ != colnames:
                            print("ERROR: number of keywords do not match"
                                  "for file {}".format(filename))
                            print("- expected:", colnames)
                            print("- required:", colnames_)
                            raise SystemExit()

                    # new_df_row = [os.path.basename(outfile)]
                    new_df_row = [outfile]
                    new_df_row += list(quantiles.values())
                    if lkeyword is not None:
                        for keyword in lkeyword:
                            new_df_row += [storedkeywords[keyword]]
                    df.loc[n-1] = new_df_row

    if img1 is not None:
        if n > 0:
            print()
    else:
        if df is not None:
            if df.shape[0] > 0:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                print(df.round(1).to_string(index=True))

    raise SystemExit()
