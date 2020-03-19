# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import json
import os

from .load_instrument_configuration import load_instrument_configuration


def delete_reduced(instrument, reducedima):
    """Delete calibration: actual file and database reference

    Parameters
    ----------
    instrument : str
        Instrument name.
    reducedima : str
        Full path and file name of the reduced calibration image.
    """
    print('Image to be deleted {}'.format(reducedima))

    # determine image type and night
    islash = reducedima.find('/')
    if islash < 0:
        msg = 'ERROR: Invalid reduced filename: {}.\nCheck for missing path'.format(reducedima)
        raise SystemError(msg)
    imagetype = reducedima[:islash]
    iislash = reducedima[(islash + 1):].find('/')
    night = reducedima[(islash + 1):(islash + 1 + iislash)]

    # load instrument configuration, determine calibration image types
    # and check that the current image type is one of them
    instconf = load_instrument_configuration(
        instrument=instrument,
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
        databasefile = 'filabres_db_{}_{}.json'.format(instrument, imagetype)
        with open(databasefile, 'w') as outfile:
            json.dump(database, outfile, indent=2)
        print('-> Updating {}'.format(databasefile))
    else:
        # ToDo: remove entry in scientific database
        pass

    # remove the actual file
    try:
        os.remove(reducedima)
        print('-> Deleting file {}'.format(reducedima))
    except:
        print("Error while deleting file : ", reducedima)
