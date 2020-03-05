# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import yaml


def load_setup(verbose=False):
    """
    Load setup file

    Parameters
    ==========
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    instrument : str
        Instrument name.
    datadir : str
        Data directory where the original FITS files are stored.
    ignored_images_file : str
        Nome of the file containing the images to be ignored.
    image_header_corrections_file : str
        Name of the file containing the image corrections.
    """

    setupfile = 'setup_filabres.yaml'
    with open(setupfile) as yamlfile:
        setupdata = yaml.load(yamlfile, Loader=yaml.SafeLoader)

    expected_kwd = ['instrument', 'datadir', 'ignored_images_file', 'image_header_corrections_file']

    for kwd in expected_kwd:
        if kwd not in setupdata:
            msg = 'Expected keyword {} missing in {}'.format(kwd, setupfile)
            raise SystemError(msg)

    for kwd in setupdata:
        if kwd not in expected_kwd:
            msg = 'Unexpected keyword {} in {}'.format(kwd, setupfile)
            raise SystemError(msg)

    instrument = setupdata['instrument']
    datadir = setupdata['datadir']
    ignored_images_file = setupdata['ignored_images_file']
    image_header_corrections_file = setupdata['image_header_corrections_file']

    if verbose:
        print('* instrument............: {}'.format(instrument))
        print('* datadir...............: {}'.format(datadir))
        print('* ignored_images_file...: {}'.format(ignored_images_file))
        print('* image_corrections_file: {}'.format(image_header_corrections_file))

    return instrument, datadir, ignored_images_file, image_header_corrections_file
