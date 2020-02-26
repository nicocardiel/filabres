import fnmatch
import glob
import json
import os
import pandas as pd

from .load_instrument_configuration import load_instrument_configuration


def list_reduced(instrument, img1, img2, args_night, args_keyword,
                 args_ndecimal=5):
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
            print('ERROR: -k KEYWORD is only valid together with -lr')
            raise SystemExit()
        else:
            lkeyword = [item[0].upper() for item in args_keyword]
    else:
        lkeyword = []

    if len(lkeyword) == 0:
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
            print('ERROR: do not use -lr and -lrf simultaneously.')
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

    # check for imagetype subdirectory
    if not os.path.isdir(imagetype):
        msg = "Subdirectory {} not found".format(imagetype)
        raise SystemError(msg)

    # selected nights to be displayed
    if args_night is None:
        night = '*'
    else:
        night = args_night

    # determine whether the imagetype is a calibration or not
    classification = \
        instconf['imagetypes'][imagetype]['classification']

    if classification == 'calibration':
        # the database of the reduced calibrations is stored in a single
        # JSON file
        expected_databasenames = ''
    else:
        # the databases of the reduced science images are stored as
        # independent JSON files
        expected_databasenames = imagetype + '/' + night + '/'
    expected_databasenames += 'filabres_db_{}_{}.json'.format(instrument,
                                                              imagetype)
    list_of_databases = glob.glob(expected_databasenames)
    list_of_databases.sort()

    n = 0
    colnames = None
    df = None  # Avoid PyCharm warning

    for jsonfilename in list_of_databases:

        try:
            with open(jsonfilename) as jfile:
                database = json.load(jfile)
        except FileNotFoundError:
            msg = 'File {} not found'.format(jsonfilename)
            raise SystemError(msg)

        if classification == 'calibration':
            for ssig in database[imagetype]:
                minidict = database[imagetype][ssig]
                for mjdobs in minidict:
                    outfile = minidict[mjdobs]['filename']
                    nightok = fnmatch.fnmatch(minidict[mjdobs]['night'], night)
                    if nightok:
                        n += 1
                        if img2 is not None:
                            print(outfile, end=' ')
                        else:
                            # show all valid keywords and exit
                            if 'ALL' in lkeyword:
                                valid_keywords = instconf['masterkeywords']
                                valid_keywords += list(minidict[mjdobs]['statsumm'].keys())
                                valid_keywords.append('NORIGIN')
                                for kwd in ['ierr_bias', 'ierr_flat']:
                                    if kwd in minidict[mjdobs]:
                                        valid_keywords.append(kwd.upper())
                                print('Valid keywords:', valid_keywords)
                                raise SystemExit()
                            storedkeywords = minidict[mjdobs]['masterkeywords']
                            storedkeywords.update(minidict[mjdobs]['statsumm'])
                            norigin = minidict[mjdobs]['norigin']
                            storedkeywords.update({'NORIGIN': norigin})
                            for kwd in ['ierr_bias', 'ierr_flat']:
                                if kwd in minidict[mjdobs]:
                                    storedkeywords.update({kwd.upper(): minidict[mjdobs][kwd]})
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
                                    print("ERROR: number of keywords do not match for file {}".format(outfile))
                                    print("- expected:", colnames)
                                    print("- required:", colnames_)
                                    raise SystemExit()

                            # new_df_row = [os.path.basename(outfile)]
                            new_df_row = [outfile]
                            if lkeyword is not None:
                                for keyword in lkeyword:
                                    new_df_row += [storedkeywords[keyword]]
                            df.loc[n-1] = new_df_row
        elif classification == 'science':
            for filename in database[imagetype]:
                minidict = database[imagetype][filename]
                outfile = minidict['filename']
                nightok = fnmatch.fnmatch(minidict['night'], night)
                if nightok:
                    n += 1
                    if img2 is not None:
                        print(outfile, end=' ')
                    else:
                        # show all valid keywords and exit
                        if 'ALL' in lkeyword:
                            valid_keywords = instconf['masterkeywords']
                            valid_keywords += list(minidict['statsumm'].keys())
                            for kwd in ['ierr_bias', 'ierr_flat']:
                                if kwd in minidict:
                                    valid_keywords.append(kwd.upper())
                            print('Valid keywords:', valid_keywords)
                            raise SystemExit()
                        storedkeywords = minidict['masterkeywords']
                        storedkeywords.update(minidict['statsumm'])
                        for kwd in ['ierr_bias', 'ierr_flat']:
                            if kwd in minidict:
                                storedkeywords.update({kwd.upper(): minidict[kwd]})
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
                                print("ERROR: number of keywords do not match for file {}".format(outfile))
                                print("- expected:", colnames)
                                print("- required:", colnames_)
                                raise SystemExit()

                        # new_df_row = [os.path.basename(outfile)]
                        new_df_row = [outfile]
                        if lkeyword is not None:
                            for keyword in lkeyword:
                                new_df_row += [storedkeywords[keyword]]
                        df.loc[n - 1] = new_df_row
        else:
            msg = 'Unexpected classification {}'.format(classification)
            raise SystemError(msg)

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
