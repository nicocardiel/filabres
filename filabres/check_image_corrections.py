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


class ImageCorrections(object):
    """
    Class to store and apply image corrections.

    Parameters
    ----------
    image_header_corrections_file : str
        Name of the file containing the image corrections.
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
        Content of the 'image_header_corrections_file'
    """

    def __init__(self, image_header_corrections_file, datadir, verbose):
        if os.path.isfile(image_header_corrections_file):
            with open(image_header_corrections_file) as yamlfile:
                self.corrections = list(yaml.load_all(yamlfile, Loader=yaml.SafeLoader))
            if verbose:
                print('\nFile {} found'.format(image_header_corrections_file))
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
                            print('- night {} has {} files with corrections'.format(night, len(list_of_files)))
                    else:
                        print('- skipping image corrections in night {}'.format(night))
                else:
                    msg = 'Missing "night" keyword in block #{} of {}'.format(i+1, image_header_corrections_file)
                    raise SystemError(msg)
        else:
            self.corrections = None
            self.nights = set()
            print('WARNING: file {} not found'.format(image_header_corrections_file))

        if verbose:
            print('Nights with image corrections: {}'.format(self.nights))

    def fixheader(self, night, basename, header, verbose=False, logfile=None):
        """
        Modify the image header if the image appears in the YAML file
        with image corrections.

        Parameters
        ----------
        night : str
            Night where the original FITS file is stored.
        basename : str
            Name of the original FITS file without the path.
        header : astropy header
            Header to be modified (if necessary).
        verbose : bool
            If True, display intermediate information.
        logfile : file handler or None
            Log file to store messages.

        Returns
        -------
        header : astropy header
            The same input FITS header after the corresponding changes.
        """
        if len(self.nights) == 0:
            return header

        if night in self.nights:
            for d in self.corrections:
                if d['night'] == night:
                    for fname in d['files']:
                        if fnmatch.fnmatch(basename, fname):
                            msg = ' -> Fixing {}'.format(basename)
                            if logfile is not None:
                                logfile.write(msg + '\n')
                            if verbose:
                                print(msg)
                            for dd in d['replace-keyword']:
                                kwd = list(dd.keys())[0]
                                kwd = kwd.upper()
                                val = dd[kwd]
                                if kwd in header:
                                    msg = '  - changing {} from {} to {}'.format(kwd, header[kwd], val)
                                    if logfile is not None:
                                        logfile.write(msg + '\n')
                                    if verbose:
                                        print(msg)
                                    header[kwd] = val
                                else:
                                    msg = 'keyword {} not found in header of {}'.format(kwd, basename)
                                    raise SystemError(msg)
        return header
