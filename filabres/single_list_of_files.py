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


def single_list_of_files(initlist, path=''):
    """
    Convert a list of files with wildcards into a single list.

    Parameters
    ==========
    initlist : list
        Initial file list. Individual entries in this list can have
        file name specifications with wildcards.
    path : str
        Path to the filename.

    Returns
    =======
    result : list
        Single list of files matching the sequence of filenames
        initially provided.
    """
    result = []
    for item in initlist:
        result += glob.glob(path + item)
    return result
