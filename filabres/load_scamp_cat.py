# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import numpy as np


def load_scamp_cat(catalogue, workdir, logfile=None):
    """
    Load X, Y coordinates from catalogue generated with SCAMP

    Parameters
    ==========
    catalogue : str
        Catalogue to be read. It must be 'full' or 'merged'.
    workdir : str
        Work subdirectory.
    logfile: instance of ToLogFile or None
        Log file to store information.

    Returns
    =======
    col1, col2 : numpy 1D arrays
        X, Y coordinates of the peaks (only if catalogue is 'full').
        RA, DEC coordinates of the peaks (only if catalogue is 'merged').
    """

    if catalogue not in ['full', 'merged']:
        msg = 'Invalid catalogue description: {}'.format(catalogue)
        raise SystemError(msg)

    fname = '{}/{}_1.cat'.format(workdir, catalogue)
    with open(fname, 'rt') as f:
        fulltxt = f.readlines()

    if logfile is not None:
        logfile.print('Reading {}'.format(fname))

    # determine relevant column numbers
    if catalogue == 'full':
        colnames = ['X_IMAGE', 'Y_IMAGE', 'CATALOG_NUMBER']
    else:
        colnames = ['ALPHA_J2000', 'DELTA_J2000']
    ncol = []
    for col in colnames:
        ii = None
        for i, line in enumerate(fulltxt):
            if col in line:
                ii = i + 1
                break
        if ii is None:
            msg = '{} not found in {}'.format(col, fname)
            raise SystemError(msg)
        if logfile is not None:
            logfile.print('{} is located in column #{}'.format(col, ii))
        ncol.append(ii - 1)

    # read full data set
    fulltable = np.genfromtxt(fname)

    if catalogue == 'full':
        # delete invalid rows (those with CATALOG_NUMBER == 0)
        valid_rows = np.where(fulltable[:, ncol[2]] != 0)[0]
        if logfile is not None:
            logfile.print('Number of objects read: {}'.format(len(valid_rows)))
        newtable = fulltable[valid_rows, :]
    else:
        newtable = fulltable

    col1 = newtable[:, ncol[0]]
    col2 = newtable[:, ncol[1]]

    return col1, col2
