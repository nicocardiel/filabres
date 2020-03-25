# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import scatter_matrix

from .ximshow import ximshow_file


def show_df(df, n, list_mode, imagetype, args_keyword_sort, args_ndecimal,
            args_plotxy, args_plotimage):
    """
    Display list, plot XY diagrams and display images.

    Parameters
    ----------
    df : pandas dataframe or None
        Dataframe with the information to be displayed.
    n : int
        Number of rows in input dataframe 'df'.
    list_mode : str
        List mode:
        - long: each file in a single line with additional keywords
        - basic: each file in a single line without the file path and
                 without additional keywords
        - singleline: all the files in a single line without additional keywords
    imagetype : str
        Image type. It should coincide with any of the available
        image types declared in the instrument configuration file.
    args_keyword_sort: list or None
        List with keywords to be used to sort the displayed table.
        If not given in args_keyword, the keywords will be appended
        to the list of displayed keywords.
    args_ndecimal : int or None
        Number of decimal places for floats.
    args_plotxy : bool
        If True, plot scatter matrices to visualize trends in the
        selected keywords.
    args_plotimage: bool
        If True, display selected images.
    """

    if args_ndecimal is None:
        ndecimal = 5
    else:
        ndecimal = args_ndecimal

    if list_mode == "singleline":
        if n > 0:
            print()
    elif list_mode == "basic":
        print('Total: {} files'.format(n))
    else:
        if df is not None:
            if df.shape[0] > 0:
                # start dataframe index at 1 instead of 0
                df.index += 1
                if args_keyword_sort is not None:
                    kwds = [item[0].upper() for item in args_keyword_sort]
                    kwds.append('file')
                    df = df.sort_values(by=kwds)
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', 10000)
                print(df.round(ndecimal).to_string(index=True))
            print('Total: {} files'.format(df.shape[0]))
        else:
            print('Total: {} files'.format(0))

        if df is not None:
            if df.shape[0] > 0:
                # scatter plots
                if args_plotxy:
                    with plt.style.context('seaborn'):
                        # remove the 'file' column and convert to float the remaining columns
                        scatter_matrix(df.drop(['file'], axis=1).astype(float, errors='ignore'))
                        print('Press "q" to continue...', end='')
                        plt.suptitle('{} ({} files)'.format(imagetype, df.shape[0]))
                        plt.tight_layout(rect=(0, 0, 1, 0.95))
                        plt.show()
                        print('')
                # display images
                if args_plotimage:
                    # preserve sorted dataframe if args_keyword_sort is not None
                    for i in df.index.values:
                        fname = df.loc[i, 'file']
                        print(df.loc[[i]].round(ndecimal).to_string(index=True))
                        with plt.style.context('seaborn'):
                            ximshow_file(fname, debugplot=12)
