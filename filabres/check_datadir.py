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
import os


def check_datadir(datadir):
    """
    Check that FITS files in DATADIR are not repeated

    Parameters
    ==========
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    """

    try:
        all_nights = os.listdir(datadir)
    except FileNotFoundError:
        print('ERROR: datadir directory {} not found'.format(datadir))
        raise SystemExit()

    all_nights.sort()

    all_files = {}
    nfiles = 0
    repeated_files = []
    for night in all_nights:
        newfiles = glob.glob(datadir + night + '/*.fits')
        for filename in newfiles:
            nfiles += 1
            basename = os.path.basename(filename)
            if basename in all_files:
                repeated_files.append(basename)
                all_files[basename].append(filename)
            else:
                all_files[basename] = [filename]
        print('Night {} -> number of files:{:6d} --> TOTAL:{:6d}'.format(night, len(newfiles), nfiles))

    if len(repeated_files) > 1:
        print('WARNING: There are repeated files!')
        input('Press <RETURN> to continue...')
        for basename in repeated_files:
            print('* File {} appears in:'.format(basename))
            for filename in all_files[basename]:
                print(filename)
    else:
        print('There are not repeated files')
