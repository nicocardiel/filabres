# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import json
import os
import pandas as pd

from .check_list_filter import check_list_filter
from .load_instrument_configuration import load_instrument_configuration
from .show_df import show_df
from .statsumm import statsumm

from filabres import LISTDIR


def list_originf(instrument, args_originf, list_mode, datadir,
                 args_keyword, args_keyword_sort, args_filter, args_plotxy,
                 args_plotimage, args_ndecimal=5):
    """
    Display initial images employed to generate a particular calibration image

    Parameters
    ----------
    instrument : str
        Instrument name.
    args_originf : str
        Full path and file name of the reduced calibration image.
    list_mode : str
        List mode:
        - long: each file in a single line with additional keywords
        - basic: each file in a single line without the file path and
                 without additional keywords
        - singleline: all the files in a single line without additional keywords
    datadir : str
        Data directory where the original FITS files are stored.
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

    if len(lkeyword) == 0:
        if list_mode == "long":
            # display at least NAXIS1 and NAXIS2
            for kwd in ['NAXIS2', 'NAXIS1']:
                if kwd not in lkeyword:
                    lkeyword.insert(0, kwd)

    # determine image type and night
    islash = args_originf.find('/')
    if islash < 0:
        msg = 'ERROR: Invalid reduced filename: {}.\nCheck for missing path'.format(args_originf)
        raise SystemError(msg)
    imagetype = args_originf[:islash]
    iislash = args_originf[(islash+1):].find('/')
    night = args_originf[(islash+1):(islash+1+iislash)]

    # load instrument configuration, determine calibration image types
    # and check that the current image type is one of them
    instconf = load_instrument_configuration(
        instrument=instrument,
        redustep=None,
        dontcheckredustep=True
    )
    if imagetype not in instconf['imagetypes'].keys():
        msg = 'Image type {} not found in instrument configuration file'.format(imagetype)
        raise SystemError(msg)
    classification = instconf['imagetypes'][imagetype]['classification']
    if classification != 'calibration':
        msg = 'ERROR: image type {} is not a calibration image'
        print(msg)
        return

    # look for the expected results database
    databasefile = 'filabres_db_{}_{}.json'.format(instrument, imagetype)
    try:
        with open(databasefile) as jfile:
            database = json.load(jfile)
    except FileNotFoundError:
        msg = 'ERROR: expected database file {} not found'.format(databasefile)
        print(msg)
        return

    if imagetype not in database:
        msg = 'ERROR: keyword {} not found in {}'.format(imagetype, databasefile)
        print(msg)
        return

    # search for originf
    originf = None
    particular_signature = None
    signatures = database[imagetype].keys()
    for signature in signatures:
        if originf is not None:
            break
        for mjd in database[imagetype][signature].keys():
            minidict = database[imagetype][signature][mjd]
            if minidict['fname'] == args_originf:
                originf = minidict['originf']
                particular_signature = signature
                break

    if originf is None:
        msg = 'ERROR: file {} not found in {}'.format(args_originf, databasefile)
        raise SystemError(msg)

    # display signature and list all reduced images with the same signature
    print('> Signature: {}'.format(particular_signature))
    print('> Available images with this signature:')
    for mjd in database[imagetype][particular_signature].keys():
        fname = database[imagetype][particular_signature][mjd]['fname']
        if fname == args_originf:
            fname += ' (*)'
        print('MJD-OBS: {}, calibration: {}'.format(mjd, fname))
    print('---')
    print('> List of individual frames:')
    print('  (involved in the computation of {})'.format(args_originf))

    # read local image database for the corresponding night
    jsonfname = LISTDIR + night + '/imagedb_{}.json'.format(instrument)
    try:
        with open(jsonfname) as jfile:
            imagedb = json.load(jfile)
    except FileNotFoundError:
        raise SystemError('File {} not found'.format(jsonfname))

    n = 0
    colnames = None
    df = None

    for fname in originf:
        if fname in imagedb[imagetype]:
            storedkeywords = imagedb[imagetype][fname]
            if args_filter is not None:
                filterok = check_list_filter(args_filter, storedkeywords)
            else:
                filterok = True
            if filterok:
                outfile = datadir + night + '/' + fname
                n += 1
                if list_mode == "singleline":
                    print(outfile, end=' ')
                elif list_mode == "basic":
                    print(' - {}'.format(os.path.basename(outfile)))
                elif list_mode == "long":
                    # show all valid keywords and exit
                    if 'ALL' in lkeyword:
                        valid_keywords = instconf['masterkeywords']
                        valid_keywords += list(statsumm(image2d=None).keys())
                        print('Valid keywords:', valid_keywords)
                        raise SystemExit()
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
                            print("ERROR: number of keywords do not match for file {}".format(fname))
                            print("- expected:", colnames)
                            print("- required:", colnames_)
                            raise SystemExit()

                    new_df_row = [outfile]
                    if lkeyword is not None:
                        for keyword in lkeyword:
                            new_df_row += [storedkeywords[keyword]]
                    df.loc[n - 1] = new_df_row
                else:
                    msg = 'Unexpected list_mode {}'.format(list_mode)
                    raise SystemError(msg)
        else:
            msg = 'ERROR: file {} not found in {}'.format(fname, jsonfname)
            raise SystemError(msg)

    show_df(df=df,
            n=n,
            list_mode=list_mode,
            imagetype=imagetype,
            args_keyword_sort=args_keyword_sort,
            args_ndecimal=args_ndecimal,
            args_plotxy=args_plotxy,
            args_plotimage=args_plotimage)
