# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import os
import yaml


class ImageCorrections(object):
    """
    Class to store and apply image corrections.

    Parameters
    ==========
    image_corrections_file : str
        Name of the file containing the image corrections.
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
        Content of the YAML 'image_correction_file'.
    """

    def __init__(self, image_corrections_file, datadir, verbose):
        if os.path.isfile(image_corrections_file):
            with open(image_corrections_file) as yamlfile:
                self.corrections = list(yaml.load_all(yamlfile, Loader=yaml.BaseLoader))
            if verbose:
                print('\nFile {} found'.format(image_corrections_file))
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
                        list_of_files = d['files']
                        for filename in list_of_files:
                            filepath = datadir + night + '/' + filename
                            if os.path.isfile(filepath):
                                pass
                            else:
                                msg = 'ERROR: file {} not found'.format(filepath)
                                raise SystemError(msg)
                        self.nights.add(night)
                        if verbose:
                            print('- night {} has {} files with corrections'.format(night, len(list_of_files)))
                    else:
                        print('- ignoring image corrections in night {}'.format(night))
                else:
                    msg = 'Missing "night" keyword in block #{} of {}'.format(i+1, image_corrections_file)
                    raise SystemError(msg)
        else:
            self.corrections = None
            self.nights = set()
            print('WARNING: file {} not found'.format(image_corrections_file))

        if verbose:
            print('Nights with image corrections: {}'.format(self.nights))

    def fixheader(self, night, basename, header, verbose):
        """
        Modify the image header if the image appears in the YAML file
        with image corrections.

        Parameters
        ==========
        night : str
            Night where the original FITS file is stored.
        basename : str
            Name of the original FITS file without the path.
        header : astropy header
            Header to be modified (if necessary).
        verbose : bool
            If True, display intermediate information.

        Returns
        =======
        header : astropy header
            The same input FITS header after the corresponding changes.
        """
        if night in self.nights:
            for d in self.corrections:
                if d['night'] == night:
                    if basename in d['files']:
                        if verbose:
                            print(' -> Fixing {}'.format(basename))
                        for dd in d['replace-keyword']:
                            kwd = list(dd.keys())[0]
                            kwd = kwd.upper()
                            val = dd[kwd]
                            if kwd in header:
                                if verbose:
                                    print('  - changing {} from {} to {}'.format(kwd, header[kwd], val))
                                header[kwd] = val
                            else:
                                msg = 'keyword {} not found in header of {}'.format(kwd, basename)
                                raise SystemError(msg)
        return header
