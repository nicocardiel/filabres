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
import yaml

from .single_list_of_files import single_list_of_files


class ImageClassification(object):
    """
    Class to store the forced image classifications.

    Parameters
    ==========
    forced_classifications_file : str
        Name of the file containing the images with forced classification.
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    verbose : bool
        If True, display intermediate information.

    Attributes
    ==========
    nights : set
        List with the nights with files that need corrections.
    corrections : list of dictionaries
        Content of the 'forced_classifications_file'.
    """

    def __init__(self, forced_classifications_file, datadir, verbose):
        if os.path.isfile(forced_classifications_file):
            with open(forced_classifications_file) as yamlfile:
                self.corrections = list(yaml.load_all(yamlfile, Loader=yaml.SafeLoader))
            if verbose:
                print('\nFile {} found'.format(forced_classifications_file))
            self.nights = set()
            for i, d in enumerate(self.corrections):
                if 'night' in d:
                    night = d['night']
                    if 'enabled' in d:
                        enabled = d['enabled']
                    else:
                        enabled = True
                    if enabled:
                        # check that the night exists
                        nightdir = datadir + night
                        if os.path.isdir(nightdir):
                            pass
                        else:
                            msg = 'Night {} not found'.format(nightdir)
                            raise SystemError(msg)
                        # check that the corresponding files also exist
                        path = datadir + night + '/'
                        list_of_files = single_list_of_files(initlist=d['files'], path=path)
                        for filepath in list_of_files:
                            if os.path.isfile(filepath):
                                pass
                            else:
                                msg = 'ERROR: file {} not found'.format(filepath)
                                raise SystemError(msg)
                        self.nights.add(night)
                        if verbose:
                            print('- night {} has {} files with forced '
                                  'classification'.format(night, len(list_of_files)))
                    else:
                        print('- skipping forced classification in night {}'.format(night))
                else:
                    msg = 'Missing "night" keyword in block #{} of {}'.format(i+1, forced_classifications_file)
                    raise SystemError(msg)
        else:
            self.corrections = None
            self.nights = set()
            print('WARNING: file {} not found'.format(forced_classifications_file))

        if verbose:
            print('Nights with images with forced classification: {}'.format(self.nights))

    def to_be_reclassified(self, night, basename):
        """
        Decide whether a particular image must be reclassified.

        Parameters
        ==========
        night : str
            Night where the original FITS file is stored.
        basename : str
            Name of the original FITS file without the path.

        Returns
        =======
        result : bool
            True if the image must be ignored.
        """
        result = None
        if len(self.nights) == 0:
            return

        if night in self.nights:
            for d in self.corrections:
                if d['night'] == night:
                    for fname in d['files']:
                        if fnmatch.fnmatch(basename, fname):
                            result = d['classification']
        return result
