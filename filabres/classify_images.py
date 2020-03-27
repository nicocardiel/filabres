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

from .check_image_classification import ImageClassification
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


def classify_images(list_of_nights, instconf, setupdata, force, verbose=False):
    """
    Generate database with relevant keywords for each night.

    Parameters
    ----------
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    setupdata : dict
        Setup data stored as a Python dictionary.
    force : bool
        If True, recompute JSON file.
    verbose : bool
        If True, display intermediate information.
    """

    datadir = setupdata['datadir']
    ignored_images_file = setupdata['ignored_images_file']
    image_header_corrections_file = setupdata['image_header_corrections_file']
    forced_classifications_file = setupdata['forced_classifications_file']

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

    # check for forced_classifications_file
    forcedclassification = ImageClassification(
        forced_classifications_file=forced_classifications_file,
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
        basefname = nightdir + '/imagedb_' + instconf['instname']
        jsonfname = basefname + '.json'
        execute_night = True
        if os.path.exists(jsonfname) and not force:
            execute_night = False
            print('File {} already exists: skipping directory.'.format(jsonfname))

        if execute_night:
            # get list of FITS files for current night
            fnames = datadir + night + '/*.fits'
            list_of_fits = glob.glob(fnames)
            list_of_fits.sort()
            if verbose:
                print(' ')
            print('* Working with night {} ({}/{}) ---> {} FITS files'.format(
                night, inight + 1, len(list_of_nights), len(list_of_fits)))

            logfname = basefname + '.log'
            logfile = open(logfname, 'wt')
            if verbose:
                print('-> Creating {}'.format(logfname))

            imagedb = {
                'metainfo': {
                    'instrument': instconf['instname'],
                    'night': night,
                    'self': {
                        'creation_date': datetime.datetime.utcnow().isoformat(),
                        'thisfile': os.getcwd() + jsonfname[1:],
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
                        verbose=verbose,
                        logfile=logfile
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
                                    msg = 'WARNING: MJD-OBS changed from' \
                                          ' {} to {:.5f} (wrong value in file {})'.format(mjdobs, tinit.mjd, filepath)
                                    print(msg)
                                    logfile.write(msg + '\n')
                        else:
                            # MJD-OBS is the basic time used to handle the image reduction
                            if keyword == 'MJD-OBS':
                                if 'JD' in header:
                                    dumdict[keyword] = header['JD'] - 2400000.5
                                    msg = 'WARNING: keyword {} is missing in file {} (set to {})'.format(
                                        keyword, basename, dumdict[keyword])
                                    print(msg)
                                    logfile.write(msg + '\n')
                                else:
                                    msg = 'ERROR: MJD-OBS not computed. Modify code here!'
                                    raise SystemError(msg)
                            else:
                                dumdict[keyword] = None
                                msg = 'WARNING: keyword {} is missing in file {} (set to None)'.format(keyword, basename)
                                print(msg)
                                logfile.write(msg + '\n')
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

                # override classification if the image must be ignored or reclassified (note: we have let
                # the image classification to be performed in order to get all the masterkeywords)
                if imgtoignore.to_be_ignored(
                        night=night,
                        basename=basename,
                        verbose=verbose
                ):
                    imagetype = 'ignored'
                else:
                    # look for a forced classification
                    imagetype_ = forcedclassification.to_be_reclassified(
                        night=night,
                        basename=basename
                    )
                    if imagetype_ is not None:
                        msg = '-> Forcing classification of {} from {} to {}'.format(basename, imagetype, imagetype_)
                        logfile.write(msg + '\n')
                        if verbose:
                            print(msg)
                        imagetype = imagetype_
                # include image in corresponding classification
                if imagetype in imagedb:
                    imagedb[imagetype][basename] = dumdict
                    msg = 'File {} ({}/{}) classified as <{}>'.format(
                        basename, ifilepath + 1, len(list_of_fits), imagetype)
                    logfile.write(msg + '\n')
                    if verbose:
                        print(msg)
                else:
                    msg = 'ERROR: unexpected image type {} in file {}'.format(imagetype, basename)
                    raise SystemError(msg)

            # update number of images
            num_doublecheck = 0
            for imagetype in imagedb:
                if imagetype != 'metainfo':
                    label = 'num_' + imagetype
                    num = len(imagedb[imagetype])
                    imagedb['metainfo'][label] = num
                    num_doublecheck += num
                    msg = '{}: {}'.format(label, num)
                    logfile.write(msg + '\n')
                    if verbose:
                        print(msg)

            imagedb['metainfo']['num_allimages'] = len(list_of_fits)
            imagedb['metainfo']['num_doublecheck'] = num_doublecheck

            # generate JSON output file
            msg = '-> Creating {}'.format(jsonfname)
            logfile.write(msg + '\n')
            if verbose:
                print(msg)
            with open(jsonfname, 'w') as outfile:
                json.dump(imagedb, outfile, indent=2)

            # double check
            if num_doublecheck != len(list_of_fits):
                print('ERROR: double check in number of files failed!')
                msg = '--> see file {}'.format(jsonfname)
                raise SystemError(msg)

            # close logfile
            logfile.close()
