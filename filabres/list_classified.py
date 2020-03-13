# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import glob
import json
import os
import pandas as pd

from .load_instrument_configuration import load_instrument_configuration
from .show_df import show_df
from .statsumm import statsumm

from filabres import LISTDIR


def list_classified(instrument, img, listmode, datadir, args_night,
                    args_keyword, args_keyword_sort, args_plotxy,
                    args_plotimage, args_ndecimal=5):
    """
    Display list with already classified images of the selected type

    Parameters
    ==========
    instrument : str
        Instrument name.
    img : str or None
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
    listmode : str
        List mode:
        - long: each file in a single line with additional keywords
        - basic: each file in a single line without the file path and
                 without additional keywords
        - singleline: all the files in a single line without additional keywords
    datadir : str
        Data directory where the original FITS files are stored.
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
    args_plotxy : bool
        If True, plot scatter matrices to visualize trends in the
        selected keywords.
    args_plotimage : bool
        If True, display selected images.
    args_ndecimal : int
        Number of decimal places for floats.
    """

    # protections
    if listmode in ["basic", "singleline"]:
        msg = None
        if args_keyword is not None:
            msg = 'ERROR: -k KEYWORD is invalid with --listmode {}'.format(listmode)
        if args_keyword_sort is not None:
            msg = 'ERROR: -ks KEYWORD is invalid with --listmode {}'.format(listmode)
        if args_plotxy:
            msg = 'ERROR: -pxy KEYWORD is invalid with --listmode {}'.format(listmode)
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
        if listmode == "long":
            # display at least NAXIS1 and NAXIS2
            for kwd in ['NAXIS2', 'NAXIS1']:
                if kwd not in lkeyword:
                    lkeyword.insert(0, kwd)

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
        ['wrong-instrument', 'ignored', 'unclassified']

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
    df = None

    for jsonfname in list_of_imagedb:

        try:
            with open(jsonfname) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            raise SystemError('File {} not found'.format(jsonfname))

        night = imagedb['metainfo']['night']
        if imagetype in imagedb:
            for fname in imagedb[imagetype]:
                outfile = datadir + night + '/' + fname
                n += 1
                if listmode == "singleline":
                    print(outfile, end=' ')
                elif listmode == "basic":
                    print(' - {}'.format(os.path.basename(outfile)))
                elif listmode == "long":
                    # show all valid keywords and exit
                    if 'ALL' in lkeyword:
                        valid_keywords = instconf['masterkeywords']
                        valid_keywords += list(statsumm(image2d=None).keys())
                        print('Valid keywords:', valid_keywords)
                        raise SystemExit()
                    storedkeywords = imagedb[imagetype][fname]
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
                    df.loc[n-1] = new_df_row
                else:
                    msg = 'Unexpected listmode {}'.format(listmode)
                    raise SystemError(msg)

    show_df(df=df,
            n=n,
            listmode=listmode,
            imagetype=imagetype,
            args_keyword_sort=args_keyword_sort,
            args_ndecimal=args_ndecimal,
            args_plotxy=args_plotxy,
            args_plotimage=args_plotimage)
