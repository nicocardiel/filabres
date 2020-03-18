# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import fnmatch
import glob
import json
import os
import pandas as pd

from .check_list_filter import check_list_filter
from .load_instrument_configuration import load_instrument_configuration
from .show_df import show_df


def list_reduced(instrument, img, list_mode, args_night, args_keyword,
                 args_keyword_sort, args_filter, args_plotxy, args_plotimage,
                 args_ndecimal=5):
    """
    Display list with already classified images of the selected type

    Parameters
    ==========
    instrument : str
        Instrument name.
    img : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
    list_mode : str
        List mode:
        - long: each file in a single line with additional keywords
        - basic: each file in a single line without the file path and
                 without additional keywords
        - singleline: all the files in a single line without additional keywords
    args_night : str or None
        Selected night
    args_keyword : list or None
        List with additional keywords to be displayed when img2
        is not None (otherwise an error is raised). Note that each
        value in this list is also a list (with a single keyword).
    args_keyword_sort : list or None
        List with keywords to be used to sort the displayed table.
        If not given in args_keyword, the keywords will be appended
        to the list of displayed keywords.
    args_filter : str
        Logical expression involving keywords to be evaluated in order to
        filter the generated list.
    args_plotxy : bool
        If True, plot scatter matrices to visualize trends in the
        selected keywords.
    args_plotimage : bool
        If True, display selected images.
    args_ndecimal : int
        Number of decimal places for floats.
    """

    # protections
    if list_mode in ["basic", "singleline"]:
        msg = None
        if args_keyword is not None:
            msg = 'ERROR: -k KEYWORD is invalid with --list_mode {}'.format(list_mode)
        if args_keyword_sort is not None:
            msg = 'ERROR: -ks KEYWORD is invalid with --list_mode {}'.format(list_mode)
        if args_plotxy:
            msg = 'ERROR: -pxy KEYWORD is invalid with --list_mode {}'.format(list_mode)
        if msg is not None:
            raise SystemError(msg)

    if args_keyword is not None:
        lkeyword = [item[0].upper() for item in args_keyword]
    else:
        lkeyword = []

    if args_keyword_sort is not None:
        for item in args_keyword_sort:
            kwd = item[0].upper()
            if kwd not in lkeyword:
                lkeyword.append(kwd)

    '''
        if len(lkeyword) == 0:
        if list_mode == "long":
            # display at least NAXIS1 and NAXIS2
            for kwd in ['NAXIS2', 'NAXIS1']:
                if kwd not in lkeyword:
                    lkeyword.insert(0, kwd)
    '''

    # load instrument configuration
    instconf = load_instrument_configuration(
        instrument=instrument,
        redustep=None,
        dontcheckredustep=True
    )

    # check imagetype is a valid reduction step
    basic_imagetypes = list(instconf['imagetypes'].keys())
    valid_imagetypes = basic_imagetypes + \
        ['wrong-' + kwd for kwd in basic_imagetypes] + \
        ['wrong-instrument', 'unclassified']

    if img is None or img == []:
        imagetype = None
    else:
        if len(img) > 1:
            print('ERROR: multiple image types given')
            imagetype = None
        else:
            imagetype = img[0]

    if imagetype is not None:
        if imagetype not in valid_imagetypes:
            print('ERROR: invalid image type: {}'.format(imagetype))
    if imagetype is None or imagetype not in valid_imagetypes:
        print('Valid imagetypes:')
        for item in valid_imagetypes:
            print('- {}'.format(item))
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

    ierr_kwd = ['ierr_bias', 'delta_mjd_bias', 'ierr_flat', 'delta_mjd_flat', 'ierr_astr']

    n = 0
    colnames = None
    df = None

    for jsonfname in list_of_databases:

        try:
            with open(jsonfname) as jfile:
                database = json.load(jfile)
        except FileNotFoundError:
            msg = 'File {} not found'.format(jsonfname)
            raise SystemError(msg)

        if classification == 'calibration':
            for ssig in database[imagetype]:
                minidict = database[imagetype][ssig]
                for mjdobs in minidict:
                    storedkeywords = minidict[mjdobs]['masterkeywords']
                    storedkeywords.update(minidict[mjdobs]['statsumm'])
                    norigin = minidict[mjdobs]['norigin']
                    storedkeywords.update({'NORIGIN': norigin})
                    for kwd in ierr_kwd:
                        if kwd in minidict[mjdobs]:
                            storedkeywords.update({kwd.upper(): minidict[mjdobs][kwd]})
                    if args_filter is not None:
                        filterok = check_list_filter(args_filter, storedkeywords)
                    else:
                        filterok = True
                    if filterok:
                        outfile = minidict[mjdobs]['fname']
                        nightok = fnmatch.fnmatch(minidict[mjdobs]['night'], night)
                        if nightok:
                            n += 1
                            if list_mode == "singleline":
                                print(outfile, end=' ')
                            elif list_mode == "basic":
                                print(' - {}'.format(os.path.basename(outfile)))
                            elif list_mode == "long":
                                # show all valid keywords and exit
                                if 'ALL' in lkeyword:
                                    valid_keywords = instconf['masterkeywords']
                                    valid_keywords += list(minidict[mjdobs]['statsumm'].keys())
                                    valid_keywords.append('NORIGIN')
                                    for kwd in ierr_kwd:
                                        if kwd in minidict[mjdobs]:
                                            valid_keywords.append(kwd.upper())
                                    print('Valid keywords:', valid_keywords)
                                    raise SystemExit()
                                colnames_ = ['file']
                                if lkeyword is not None:
                                    for keyword in lkeyword:
                                        if keyword not in storedkeywords:
                                            print('ERROR: keyword {} is not stored in the image '
                                                  'database'.format(keyword))
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
                            else:
                                msg = 'Unexpected list_mode {}'.format(list_mode)
                                raise SystemError(msg)
        elif classification == 'science':
            for fname in database[imagetype]:
                minidict = database[imagetype][fname]
                outfile = minidict['fname']
                nightok = fnmatch.fnmatch(minidict['night'], night)
                if nightok:
                    n += 1
                    if list_mode == "singleline":
                        print(outfile, end=' ')
                    elif list_mode == "basic":
                        print(' - {}'.format(os.path.basename(outfile)))
                    elif list_mode == "long":
                        # show all valid keywords and exit
                        if 'ALL' in lkeyword:
                            valid_keywords = instconf['masterkeywords']
                            valid_keywords += list(minidict['statsumm'].keys())
                            for kwd in ierr_kwd:
                                if kwd in minidict:
                                    valid_keywords.append(kwd.upper())
                            print('Valid keywords:', valid_keywords)
                            raise SystemExit()
                        storedkeywords = minidict['masterkeywords']
                        storedkeywords.update(minidict['statsumm'])
                        for kwd in ierr_kwd:
                            if kwd in minidict:
                                storedkeywords.update({kwd.upper(): minidict[kwd]})
                        colnames_ = []
                        if lkeyword is not None:
                            for keyword in lkeyword:
                                if keyword not in storedkeywords:
                                    print('ERROR: keyword {} is not stored in the image database'.format(keyword))
                                    raise SystemExit()
                                colnames_ += [keyword]
                        colnames_ += ['file']
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
                        new_df_row = []
                        if lkeyword is not None:
                            for keyword in lkeyword:
                                new_df_row += [storedkeywords[keyword]]
                        new_df_row += [outfile]
                        df.loc[n - 1] = new_df_row
                    else:
                        msg = 'Unexpected list_mode {}'.format(list_mode)
                        raise SystemError(msg)
        else:
            msg = 'Unexpected classification {}'.format(classification)
            raise SystemError(msg)

    show_df(df=df,
            n=n,
            list_mode=list_mode,
            imagetype=imagetype,
            args_keyword_sort=args_keyword_sort,
            args_ndecimal=args_ndecimal,
            args_plotxy=args_plotxy,
            args_plotimage=args_plotimage)
