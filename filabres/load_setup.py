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
    ----------
    verbose : bool
        If True, display intermediate information.

    Returns
    -------
    setupdata : dict
        Dictionary containing the content of the setup file.
    """

    setupfile = 'setup_filabres.yaml'
    with open(setupfile) as yamlfile:
        setupdata = yaml.load(yamlfile, Loader=yaml.SafeLoader)

    expected_kwd = ['instrument', 'datadir', 'gaiadr_source', 'ignored_images_file',
                    'image_header_corrections_file', 'forced_classifications_file']
    additional_kwd = ['default_param', 'config_sex', 'config_scamp']

    for kwd in expected_kwd:
        if kwd not in setupdata:
            msg = 'Expected keyword {} missing in {}'.format(kwd, setupfile)
            raise SystemError(msg)
        else:
            if verbose:
                print('* {}: {}'.format(kwd, setupdata[kwd]))

    for kwd in setupdata:
        if kwd not in expected_kwd + additional_kwd:
            msg = 'Unexpected keyword {} in {}'.format(kwd, setupfile)
            raise SystemError(msg)

    return setupdata
