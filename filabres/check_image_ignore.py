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


class ImageIgnore(object):
    """
    Class to store the images that should be ignored.

    Parameters
    ----------
    ignored_images_file : str
        Name of the file containing the images to be ignored.
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    verbose : bool
        If True, display intermediate information.

    Attributes
    ----------
    nights : set
        List with the nights with files that need corrections.
    corrections : list of dictionaries
        Content of the 'ignored_images_file'.
    """

    def __init__(self, ignored_images_file, datadir, verbose):
        if os.path.isfile(ignored_images_file):
            with open(ignored_images_file) as yamlfile:
                self.corrections = list(yaml.load_all(yamlfile, Loader=yaml.SafeLoader))
            if verbose:
                print('\nFile {} found'.format(ignored_images_file))
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
                            print('- night {} has {} files to be ignored'.format(night, len(list_of_files)))
                    else:
                        print('- skipping image ignore in night {}'.format(night))
                else:
                    msg = 'Missing "night" keyword in block #{} of {}'.format(i+1, ignored_images_file)
                    raise SystemError(msg)
        else:
            self.corrections = None
            self.nights = set()
            print('WARNING: file {} not found'.format(ignored_images_file))

        if verbose:
            print('Nights with images to be ignored: {}'.format(self.nights))

    def to_be_ignored(self, night, basename, verbose=False, logfile=None):
        """
        Decide whether a particular image must be ignored.

        Parameters
        ----------
        night : str
            Night where the original FITS file is stored.
        basename : str
            Name of the original FITS file without the path.
        verbose : bool
            If True, display intermediate information.
        logfile : file handler or None
            Log file to store messages.
        Returns
        -------
        result : bool
            True if the image must be ignored.
        """
        result = False
        if len(self.nights) == 0:
            return

        if night in self.nights:
            for d in self.corrections:
                if d['night'] == night:
                    for fname in d['files']:
                        if fnmatch.fnmatch(basename, fname):
                            result = True
                            msg = ' -> Ignoring {}'.format(basename)
                            if logfile is not None:
                                logfile.write(msg + '\n')
                            if verbose:
                                print(msg)
        return result
