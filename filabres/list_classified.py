import glob
import json
import os
import pandas as pd

from .load_instrument_configuration import load_instrument_configuration

from filabres import LISTDIR


def list_classified(instrument, img1, img2, datadir, args_night,
                    args_keyword, args_ndecimal=5):
    """
    Display list with already classified images of the selected type

    Parameters
    ==========
    instrument : str
        Instrument name.
    img1 : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
        Each file name is displayed in a different line, together
        with the quantile information.
    img2 : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
        The file names are listed in a single line, separated by a
        single blank space.
    datadir : str
        Data directory where the original FITS files are stored.
    args_night : str or None
        Selected night
    args_keyword : list or None
        List with additional keywords to be displayed when img2
        is not None (otherwise an error is raised). Note that each
        value in this list is also a list (with a single keyword).
    args_ndecimal : int
        Number of decimal places for floats.
    """

    # protections
    if args_keyword is not None:
        if img1 is None:
            print('ERROR: -k KEYWORD is only valid together with -lc')
            raise SystemExit()
        else:
            lkeyword = [item[0].upper() for item in args_keyword]
    else:
        lkeyword = []

    if lkeyword == []:
        # display at least NAXIS1 and NAXIS2
        for kwd in ['NAXIS2', 'NAXIS1']:
            if kwd not in lkeyword:
                lkeyword.insert(0, kwd)

    if img2 is None:
        if img1 is None:
            return
        else:
            imagetype = img1
    else:
        if img1 is None:
            imagetype = img2
        else:
            print('ERROR: do not use -lc and -lcf simultaneously.')
            raise SystemExit()

    # load instrument configuration
    instconf = load_instrument_configuration(
        instrument=instrument,
        redustep=imagetype,
        dontcheckredustep=True
    )

    # check imagetype is a valid reduction step
    basic_imagetypes = list(instconf['imagetypes'].keys())
    valid_imagetypes = basic_imagetypes + \
                       ['wrong-' + kwd for kwd in basic_imagetypes] + \
                       ['wrong-instrument', 'unclassified']
    if imagetype not in valid_imagetypes:
        print('ERROR: invalid image type: {}'.format(imagetype))
        raise SystemExit()

    # check for ./lists subdirectory
    if not os.path.isdir(LISTDIR):
        msg = "Subdirectory {} not found".format(LISTDIR)
        raise SystemError(msg)

    if args_night is None:
        night = '*'
    else:
        night = args_night

    list_of_imagedb = glob.glob(LISTDIR + night + '/imagedb_*.json')
    list_of_imagedb.sort()

    n = 0
    colnames = None
    df = None  # Avoid PyCharm warning

    for jsonfilename in list_of_imagedb:

        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            raise SystemError('File {} not found'.format(jsonfilename))

        night = imagedb['metainfo']['night']
        if imagetype in imagedb:
            for filename in imagedb[imagetype]:
                outfile = datadir + night + '/' + filename
                n += 1
                if img2 is not None:
                    print(outfile, end=' ')
                else:
                    # show all valid keywords and exit
                    if 'ALL' in lkeyword:
                        valid_keywords = instconf['masterkeywords']
                        valid_keywords += instconf['quantkeywords']
                        print('Valid keywords:', valid_keywords)
                        raise SystemExit()
                    storedkeywords = imagedb[imagetype][filename]
                    colnames_ = ['file']
                    if lkeyword is not None:
                        for keyword in lkeyword:
                            if keyword not in storedkeywords:
                                print('ERROR: keyword {} is not stored in the image database'.format(keyword))
                                raise SystemExit()
                            colnames_ += [keyword]
                    if n == 1:
                        colnames = colnames_
                        df = pd.DataFrame(columns=colnames)
                    else:
                        if colnames_ != colnames:
                            print("ERROR: number of keywords do not match for file {}".format(filename))
                            print("- expected:", colnames)
                            print("- required:", colnames_)
                            raise SystemExit()

                    # new_df_row = [os.path.basename(outfile)]
                    new_df_row = [outfile]
                    if lkeyword is not None:
                        for keyword in lkeyword:
                            new_df_row += [storedkeywords[keyword]]
                    df.loc[n-1] = new_df_row

    if img2 is not None:
        if n > 0:
            print()
    else:
        if df is not None:
            if df.shape[0] > 0:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', -1)
                print(df.round(args_ndecimal).to_string(index=False))
            print('Total: {} files'.format(df.shape[0]))
        else:
            print('Total: {} files'.format(0))
    raise SystemExit()
