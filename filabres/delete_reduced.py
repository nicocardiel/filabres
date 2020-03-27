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
import json
import os

from .load_instrument_configuration import load_instrument_configuration


def delete_reduced(setupdata, reducedima):
    """Delete calibration: actual file and database reference

    Parameters
    ----------
    setupdata : dict
        Setup data stored as a Python dictionary.
    reducedima : str
        Full path and file name of the reduced calibration image.
    """

    instrument = setupdata['instrument']

    print('Image to be deleted {}'.format(reducedima))

    # determine image type and night
    islash = reducedima.find('/')
    if islash < 0:
        msg = 'ERROR: Invalid reduced filename: {}.\nCheck for missing path'.format(reducedima)
        raise SystemError(msg)
    imagetype = reducedima[:islash]
    iislash = reducedima[(islash + 1):].find('/')
    night = reducedima[(islash + 1):(islash + 1 + iislash)]
    basename = reducedima[(islash + 1 + iislash + 1):]
    idum1 = basename.find(imagetype)
    idum2 = basename.find('_red.fits')
    original_basename = basename[(idum1 + 1 + len(imagetype)):idum2] + '.fits'

    # load instrument configuration, determine calibration image types
    # and check that the current image type is one of them
    instconf = load_instrument_configuration(
        setupdata=setupdata,
        redustep=None,
        dontcheckredustep=True
    )
    if imagetype not in instconf['imagetypes'].keys():
        msg = 'Image type {} not found in instrument configuration file'.format(imagetype)
        raise SystemError(msg)
    classification = instconf['imagetypes'][imagetype]['classification']

    if classification == 'calibration':
        # look for the expected results database
        databasefile = 'filabres_db_{}_{}.json'.format(instrument, imagetype)
        try:
            with open(databasefile) as jfile:
                database = json.load(jfile)
        except FileNotFoundError:
            msg = 'ERROR: expected database file {} not found'.format(databasefile)
            print(msg)
            return

        if imagetype not in database:
            msg = 'ERROR: keyword {} not found in {}'.format(imagetype, databasefile)
            print(msg)
            return

        # search for mjd
        particular_mjd = None
        particular_signature = None
        signatures = database[imagetype].keys()
        for signature in signatures:
            if particular_mjd is not None:
                break
            for mjd in database[imagetype][signature].keys():
                minidict = database[imagetype][signature][mjd]
                if minidict['fname'] == reducedima:
                    particular_mjd = mjd
                    particular_signature = signature
                    break

        if particular_mjd is None:
            msg = 'ERROR: file {} not found in {}'.format(reducedima, databasefile)
            raise SystemError(msg)

        # display signature and modified Julian Date
        print('Signature: {}'.format(particular_signature))
        print('MJD-OBS..: {}'.format(particular_mjd))

        ncal_with_signature = len(database[imagetype][particular_signature])
        print('Number of reduced {} images with this signature: {}'.format(imagetype, ncal_with_signature))
        if ncal_with_signature > 1:
            del database[imagetype][particular_signature][particular_mjd]
        elif ncal_with_signature == 1:
            del database[imagetype][particular_signature]
            print('-> Deleting entry in {}'.format(databasefile))
        else:
            msg = 'ERROR: unexpected number of calibration images with ' \
                  'required signature = {}'.format(ncal_with_signature)
            raise SystemError(msg)

        # save new updated database
        with open(databasefile, 'w') as outfile:
            json.dump(database, outfile, indent=2)
        print('-> Updating {}'.format(databasefile))
    elif classification == 'science':
        # look for the expected results database
        databasefile = '{}/{}/filabres_db_{}_{}.json'.format(imagetype, night, instrument, imagetype)
        try:
            with open(databasefile) as jfile:
                database = json.load(jfile)
        except FileNotFoundError:
            msg = 'ERROR: expected database file {} not found'.format(databasefile)
            print(msg)
            return

        if imagetype not in database:
            msg = 'ERROR: keyword {} not found in {}'.format(imagetype, databasefile)
            print(msg)
            return

        if original_basename not in database[imagetype]:
            msg = 'ERROR: filename {} not found in {}'.format(original_basename, databasefile)
            print(msg)
            return

        # remove database entry
        del database[imagetype][original_basename]
        print('-> Deleting entry in {}'.format(databasefile))

        # save new updated database
        with open(databasefile, 'w') as outfile:
            json.dump(database, outfile, indent=2)
        print('-> Updating {}'.format(databasefile))
    else:
        msg = 'ERROR: unexpected classification: {}'.format(classification)
        raise SystemError(msg)

    # remove the actual file
    try:
        os.remove(reducedima)
        print('-> Deleting file: {}'.format(reducedima))
    except:
        print("Error while deleting file : ", reducedima)

    # remove auxiliary subdirectory
    if classification == 'science':
        idum = reducedima.find('.fits')
        subdir = reducedima[:idum]
        filelist = glob.glob('{}/*'.format(subdir))
        for filepath in filelist:
            try:
                os.remove(filepath)
                print('-> Removing file: {}'.format(filepath))
            except:
                print("ERROR while deleting file: ".format(filepath))
        # remove subdirectory
        try:
            os.rmdir(subdir)
            print('-> Removing subdirectory: {}'.format(subdir))
        except:
            print("ERROR while deleting subdirectory: {}".format(subdir))
