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
import os


def nights_to_be_reduced(args_night, setupdata, verbose=False):
    """Generate list of nights to be reduced.

    Parameters
    ----------
    args_night : str or None
        Night label. Wildcards are valid. If None, all the nights
        within the datadir directory are considered.
    setupdata : dict
        Setup data stored as a Python dictionary.
    verbose : bool
        If True, display intermediate information.

    Returns
    -------
    list_of_nights : list
        List of nights matching the selection filter.

    """

    datadir = setupdata['datadir']

    if args_night is None:
        night = '*'
    else:
        night = args_night

    try:
        all_nights = os.listdir(datadir)
    except FileNotFoundError:
        print('ERROR: directory {} not found'.format(datadir))
        raise SystemExit()

    all_nights.sort()
    if '.DS_Store' in all_nights:
        all_nights.remove('.DS_Store')

    list_of_nights = [fname for fname in all_nights if fnmatch.fnmatch(fname, night)]

    if len(list_of_nights) == 0:
        print('ERROR: no subdirectory matches the night selection')
        raise SystemExit()

    list_of_nights.sort()

    print('* Number of nights found: {}'.format(len(list_of_nights)))
    if verbose:
        print('* List of nights: {}'.format(list_of_nights))

    return list_of_nights
