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

from .check_image_ignore import ImageIgnore


def check_datadir(datadir, ignored_images_file, verbose=False):
    """
    Check that FITS files in DATADIR are not repeated

    Parameters
    ==========
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    ignored_images_file : str
        Nome of the file containing the images to be ignored.
    verbose : bool
        If True, display intermediate information.
    """

    try:
        all_nights = os.listdir(datadir)
    except FileNotFoundError:
        print('ERROR: datadir directory {} not found'.format(datadir))
        raise SystemExit()

    # check for ignored_images_file
    imgtoignore = ImageIgnore(
        ignored_images_file=ignored_images_file,
        datadir=datadir,
        verbose=verbose
    )

    all_nights.sort()

    all_files = {}
    nfiles = 0
    repeated_files = []
    for night in all_nights:
        newfiles = glob.glob(datadir + night + '/*.fits')
        nignored = 0
        for fname in newfiles:
            basename = os.path.basename(fname)
            if not imgtoignore.to_be_ignored(
                    night=night,
                    basename=basename,
                    verbose=verbose
            ):
                nfiles += 1
                if basename in all_files:
                    repeated_files.append(basename)
                    all_files[basename].append(fname)
                else:
                    all_files[basename] = [fname]
            else:
                nignored += 1
        print('Night {} -> number of files:{:6d}, ignored:{:6d} --> TOTAL:{:6d}'.format(
            night, len(newfiles), nignored, nfiles))

    if len(repeated_files) > 1:
        print('WARNING: There are repeated files!')
        input('Press <ENTER> to display duplicate files...')
        for basename in repeated_files:
            print('\n* File {} appears in:'.format(basename))
            for fname in all_files[basename]:
                print(fname)
    else:
        print('There are not repeated files')
