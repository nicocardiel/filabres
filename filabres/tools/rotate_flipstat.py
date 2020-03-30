# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

"""
Rotate LSSS image by 180 degrees and change the value of the
keyword FLIPSTAT.
"""

import argparse
from astropy.io import fits
import numpy as np


def main():
    # parse command-line options
    parser = argparse.ArgumentParser(description="Auxiliary script to rotate LSSS images")

    parser.add_argument("filename", help="input FITS file")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # ---

    # determine FITS extension
    if args.filename[-5:] == '.fits':
        extension = '.fits'
    elif args.filename[-4:] == '.fts':
        extension = '.fts'
    else:
        msg = 'ERROR: FITS extension (.fits / .fts) not found!'
        raise SystemError(msg)

    # set output file name
    output_filename = args.filename[:-5] + 'r' + extension
    if args.debug:
        print('Output file name: {}'.format(output_filename))

    with fits.open(args.filename) as hdul:
        header = hdul[0].header
        data = hdul[0].data

    # update keyword FLIPSTAT
    flipstat = header['flipstat']
    if args.debug:
        print('Initial FLIPSTAT: -->{}<--'.format(flipstat))
    if flipstat == '':
        newflipstat = 'Flip/Mirror'
    elif flipstat == 'Flip/Mirror':
        newflipstat = ''
    else:
        msg = 'ERROR: unexpected FLIPSTAT value: -->{}<--'.format(flipstat)
        raise SystemError(msg)
    header['flipstat'] = newflipstat
    if args.debug:
        print('Final FLIPSTAT..: -->{}<--'.format(newflipstat))

    # rotate image by 180 degrees (using two flip calls in alternate axis)
    newdata = np.flip(np.flip(data, 1), 0)

    # generate output file
    hdu = fits.PrimaryHDU(newdata.astype(np.float32), header)
    hdu.writeto(output_filename, overwrite=True)


if __name__ == "__main__":

    main()
