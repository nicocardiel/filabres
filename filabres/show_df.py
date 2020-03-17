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


def show_df(df, n, listmode, imagetype, args_keyword_sort, args_ndecimal,
            args_plotxy, args_plotimage):
    if listmode == "singleline":
        if n > 0:
            print()
    elif listmode == "basic":
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
                pd.set_option('display.max_colwidth', -1)
                print(df.round(args_ndecimal).to_string(index=True))
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
                    for i in range(df.shape[0]):
                        fname = df['file'].values[i]
                        print(df.loc[[i+1]].round(args_ndecimal).to_string(index=True))
                        with plt.style.context('seaborn'):
                            ximshow_file(fname, debugplot=12)
