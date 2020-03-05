# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from astropy.io import fits
from astropy.time import Time
import datetime
import glob
import json
import os
import sys
import uuid
import warnings

from .check_image_corrections import ImageCorrections
from .check_image_ignore import ImageIgnore
from .progressbar import progressbar
from .statsumm import statsumm
from .version import version

from filabres import LISTDIR
from filabres import REQ_OPERATORS


def check_requirements(requirements, header, dictquant):
    """
    Check requirements.

    Parameters
    ==========
    requirements : list
        List of requirements.
    header: astropy `Header` object
        Image header.
    dictquant : dict
        Measured quantiles in the image.

    Returns
    =======
    result : bool
        True if all the requirements are met.
    """

    result = True

    for keyword in requirements:
        operatorfound = False
        for operator in REQ_OPERATORS:
            lenop = len(operator)
            if keyword[-lenop:] == operator:
                operatorfound = True
                newkeyword = keyword[:-lenop]
                if newkeyword in dictquant:
                    command = 'dictquant[newkeyword] '
                else:
                    command = 'header[newkeyword] '
                command += REQ_OPERATORS[operator]
                command += ' requirements[keyword]'
                if not eval(command):
                    result = False
                break
        if not operatorfound:
            if isinstance(requirements[keyword], str):
                if requirements[keyword].lower() != header[keyword].lower():
                    result = False
            elif isinstance(requirements[keyword], int):
                if requirements[keyword] != header[keyword]:
                    result = False
            elif isinstance(requirements[keyword], float):
                if requirements[keyword] != header[keyword]:
                    result = False
            else:
                msg = 'Codify comparison here for {}'.format(
                    type(requirements[keyword]))
                raise SystemError(msg)

        if not result:
            break

    return result


def classify_image(instconf, header, dictquant):
    """
    Classify image in one of the expected types.

    The classification also checks that the specific requirements set
    to each image type are also met.
    Note that the function returns the first image type match without
    checking for additional potential matches.

    Parameters
    ----------
    instconf : dict
        Instrument configuration.
        for details.
    header: astropy `Header` object
        Image header.
    dictquant : dict
        Measured quantiles in the image.

    Returns
    -------
    imagetype : str or None
        One of the expected image types (or None if the any of the
        requirements is not met).
    """

    imagetype = None

    # check mandatory requirements
    for img in instconf['imagetypes']:
        requirements = instconf['imagetypes'][img]['requirements']
        typefound = check_requirements(requirements, header, dictquant)
        if typefound:
            imagetype = img
            break

    if imagetype is None:
        return imagetype

    # after having found a valid initial imagetype, check the additional
    # requirements for this particular imagetype; if any of them fails,
    # add the prefix 'wrong-' to the initial imagetype
    requirementx = instconf['imagetypes'][imagetype]['requirementx']
    if len(requirementx) == 0:
        return imagetype
    typefound = check_requirements(requirementx, header, dictquant)

    if not typefound:
        imagetype = 'wrong-' + imagetype

    return imagetype


def initialize_auxdb(list_of_nights, instconf, datadir, force,
                     ignored_images_file, image_header_corrections_file, verbose=False):
    """
    Generate database with relevant keywords for each night.

    Parameters
    ----------
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    datadir : str
        Directory where the original FITS data (organized by night)
        are stored.
    force : bool
        If True, recompute JSON file.
    ignored_images_file : str
        Name of the file containing the images to be ignored.
    image_header_corrections_file : str
        Name of the file containing the image corrections.
    verbose : bool
        If True, display intermediate information.
    """

    # check for ignored_images_file
    imgtoignore = ImageIgnore(
        ignored_images_file=ignored_images_file,
        datadir=datadir,
        verbose=verbose
    )

    # check for image_header_corrections_file
    imgcorrections = ImageCorrections(
        image_header_corrections_file=image_header_corrections_file,
        datadir=datadir,
        verbose=verbose
    )

    # check for ./lists subdirectory
    if os.path.isdir(LISTDIR):
        if verbose:
            print('\nSubdirectory {} found'.format(LISTDIR))
    else:
        if verbose:
            print('\nSubdirectory {} not found. Creating it!'.format(LISTDIR))
        os.makedirs(LISTDIR)

    # create one subdirectory for each night
    for inight, night in enumerate(list_of_nights):
        # subdirectory for current night
        nightdir = LISTDIR + night
        if os.path.isdir(nightdir):
            if verbose:
                print('Subdirectory {} found'.format(nightdir))
        else:
            if verbose:
                print('Subdirectory {} not found. Creating it!'.format(nightdir))
            os.makedirs(nightdir)

        # generate database for all the files in current night
        basefilename = nightdir + '/imagedb_' + instconf['instname']
        jsonfilename = basefilename + '.json'
        execute_night = True
        if os.path.exists(jsonfilename) and not force:
            execute_night = False
            print('File {} already exists: skipping directory.'.format(jsonfilename))

        if execute_night:
            # get list of FITS files for current night
            filenames = datadir + night + '/*.fits'
            list_of_fits = glob.glob(filenames)
            list_of_fits.sort()
            if verbose:
                print(' ')
            print('* Working with night {} ({}/{}) ---> {} FITS files'.format(
                night, inight + 1, len(list_of_nights), len(list_of_fits)))

            logfilename = basefilename + '.log'
            logfile = None
            imagedb = {
                'metainfo': {
                    'instrument': instconf['instname'],
                    'night': night,
                    'self': {
                        'creation_date': datetime.datetime.utcnow().isoformat(),
                        'thisfile': os.getcwd() + jsonfilename[1:],
                        'origin': sys.argv[0] + ', v.' + version,
                        'uuid': str(uuid.uuid1()),
                    },
                    'instconf': instconf
                }
            }

            # initalize an empty dictionary for each possible image category
            for imagetype in instconf['imagetypes']:
                imagedb[imagetype] = dict()
                imagedb['wrong-' + imagetype] = dict()
            imagedb['ignored'] = dict()
            imagedb['unclassified'] = dict()
            imagedb['wrong-instrument'] = dict()

            # get relevant keywords for each FITS file and classify it
            for ifilepath, filepath in enumerate(list_of_fits):
                if not verbose:
                    progressbar(ifilepath + 1, len(list_of_fits))
                # get image header
                basename = os.path.basename(filepath)
                dumdict = dict()
                if not imgtoignore.to_be_ignored(
                        night=night,
                        basename=basename,
                        verbose=verbose
                ):
                    warningsfound = False
                    # initially convert warnings into errors
                    warnings.filterwarnings('error')
                    header = None
                    data = None
                    try:
                        with fits.open(filepath) as hdul:
                            header = hdul[0].header
                            data = hdul[0].data
                    except (UserWarning, ResourceWarning) as e:
                        if logfile is None:
                            logfile = open(logfilename, 'wt')
                            print('-> Creating {}'.format(logfilename))
                        logfile.write('{} while reading {}\n'.format(type(e).__name__, basename))
                        logfile.write('{}\n'.format(e))
                        print('{} while reading {}'.format(
                            type(e).__name__, basename))
                        print(str(e))
                        warningsfound = True
                        # ignore warnings from here to avoid the messages:
                        # Exception ignored in:...
                        # ResourceWarning: unclosed file...
                        warnings.filterwarnings('ignore')
                    if warningsfound:
                        # ignore warnings
                        with fits.open(filepath) as hdul:
                            header = hdul[0].header
                            data = hdul[0].data
                    # check general instrument requirements
                    requirements = instconf['requirements']
                    fileok = True
                    for keyword in requirements:
                        if requirements[keyword] != header[keyword]:
                            fileok = False
                    if fileok:
                        # check if the image header needs corrections
                        header = imgcorrections.fixheader(
                            night=night,
                            basename=basename,
                            header=header,
                            verbose=verbose
                        )
                        # get master keywords for the current file
                        for keyword in instconf['masterkeywords']:
                            if keyword in header:
                                dumdict[keyword] = header[keyword]
                                # ----------------------------------------
                                # Fix here any problem with keyword values
                                # ----------------------------------------
                                # Fix negative MJD-OBS
                                if keyword == 'MJD-OBS':
                                    mjdobs = header[keyword]
                                    if mjdobs < 0:
                                        tinit = Time(header['DATE-OBS'],
                                                     format='isot', scale='utc')
                                        dumdict['MJD-OBS'] = tinit.mjd
                                        print('WARNING: MJD-OBS changed from {} to {:.5f} (wrong value in file '
                                              '{})'.format(mjdobs, tinit.mjd, filepath))
                            else:
                                msg = 'ERROR: keyword {} is missing in file {}'.format(keyword, basename)
                                raise SystemError(msg)
                        # basic image statistics
                        dictquant = statsumm(data, rm_nan=True)
                        for qkw in dictquant.keys():
                            dumdict[qkw] = dictquant[qkw]
                        # classify image
                        imagetype = classify_image(instconf, header, dictquant)
                        if imagetype is None:
                            imagetype = 'unclassified'
                    else:
                        imagetype = 'wrong-instrument'
                else:
                    imagetype = 'ignored'

                # include image in corresponding classification
                if imagetype in imagedb:
                    imagedb[imagetype][basename] = dumdict
                    if verbose:
                        print('File {} ({}/{}) classified as <{}>'.format(
                            basename, ifilepath + 1, len(list_of_fits),
                            imagetype))
                else:
                    msg = 'ERROR: unexpected image type {} in file {}'.format(imagetype, basename)
                    raise SystemError(msg)

            # close logfile (if opened)
            if logfile is not None:
                logfile.close()

            # update number of images
            num_doublecheck = 0
            for imagetype in imagedb:
                if imagetype != 'metainfo':
                    label = 'num_' + imagetype
                    num = len(imagedb[imagetype])
                    imagedb['metainfo'][label] = num
                    num_doublecheck += num
                    if verbose:
                        print('{}: {}'.format(label, num))

            imagedb['metainfo']['num_allimages'] = len(list_of_fits)
            imagedb['metainfo']['num_doublecheck'] = num_doublecheck

            # generate JSON output file
            if verbose:
                print('-> Creating {}'.format(jsonfilename))
            with open(jsonfilename, 'w') as outfile:
                json.dump(imagedb, outfile, indent=2)

            # double check
            if num_doublecheck != len(list_of_fits):
                print('ERROR: double check in number of files failed!')
                msg = '--> see file {}'.format(jsonfilename)
                raise SystemError(msg)
