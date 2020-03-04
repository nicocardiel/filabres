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


def nights_to_be_reduced(args_night, datadir, verbose=False):
    """Generate list of nights to be reduced.

    Parameters
    ----------
    args_night : str or None
        Night label. Wildcards are valid. If None, all the nights
        within the datadir directory are considered.
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    verbose : bool
        If True, display intermediate information.

    Returns
    -------
    list_of_nights : list
        List of nights matching the selection filter.

    """

    if args_night is None:
        night = '*'
    else:
        night = args_night

    try:
        all_nights = os.listdir(datadir)
    except FileNotFoundError:
        print('ERROR: directory {} not found'.format(datadir))
        raise SystemExit()

    list_of_nights = [filename for filename in all_nights if fnmatch.fnmatch(filename, night)]

    if len(list_of_nights) == 0:
        print('ERROR: no subdirectory matches the night selection')
        raise SystemExit()

    list_of_nights.sort()

    print('* Number of nights found: {}'.format(len(list_of_nights)))
    if verbose:
        print('* List of nights: {}'.format(list_of_nights))

    return list_of_nights
