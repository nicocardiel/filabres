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
import json
import numpy as np

from .signature import signature_string


def find_nearest(arraylike, value):
    """
    Find nearest value within a 1D numpy array.

    Parameters
    ==========
    arraylike : array like object
        Array object.
    value : float
        Value to be sought.

    Returns
    =======
    ipos : int
        Closest location to 'value'.
    """

    array = np.asarray(arraylike)
    ipos = (np.abs(array - value)).argmin()
    return ipos


def findclosestquant(mjdobs, database, quantile):
    """Return quantile from closest image in MJD-OBS

    Parameters
    ==========
    mjdobs : float
        MJD-OBS for which the quantile is requested.
    database : dict
        Database with the different signatures for the corresponding
        calibration images.
    quantile : str
        Quantile being sought.

    Returns
    =======
    delta_mjdobs : float
        Time interval (days) between the desired MJD-OBS and the one
        corresponding to the retrieved calibration.
    result : float
        Requested quantile value
    """
    result = None
    delta_mjdobs = None
    delta_mjdobs_abs = None
    for ssig in database.keys():
        for smjd in database[ssig].keys():
            mjdobs_ = float(smjd)
            if result is None:
                delta_mjdobs = mjdobs_ - mjdobs
                delta_mjdobs_abs = abs(delta_mjdobs)
                result = database[ssig][smjd]['statsumm'][quantile]
            else:
                if abs(mjdobs - mjdobs_) < delta_mjdobs_abs:
                    delta_mjdobs = mjdobs_ - mjdobs
                    delta_mjdobs_abs = abs(delta_mjdobs)
                    result = database[ssig][smjd]['statsumm'][quantile]
    return delta_mjdobs, result


def retrieve_calibration(instrument, redustep, signature, mjdobs, logfile):
    """
    Retrieve calibration from main database.

    Parameters
    ----------
    instrument : string
        Instrument name.
    redustep : string
        Reduction step.
    signature : dict()
        Signature of the image to be calibrated. The selected
        calibration must have the expected signature.
    mjdobs: float
        Modified Julian Date, use to locate the closest calibration
        available in the main database.
    logfile : instance of ToLogFile
        Logfile to store the output.

    Returns
    -------
    ierr : int
        Error status value. 0: no error. 1: calibration not found.
    delta_mjd : float
        Time interval (days) between the desired MJD-OBS and the one
        corresponding to the retrieved calibration.
    image2d_cal : numpy 2D array
        Numpy array with the calibration data.
    calfname: str
        Calibration file name
    """

    # expected size of calibration image
    if 'NAXIS1' in signature:
        naxis1_ = signature['NAXIS1']
    else:
        naxis1_ = None
    if 'NAXIS2' in signature:
        naxis2_ = signature['NAXIS2']
    else:
        naxis2_ = None

    # check that the requested calibration is available in the corresponding
    # calibration database
    databasefile = 'filabres_db_{}_{}.json'.format(instrument, redustep)
    try:
        with open(databasefile) as jfile:
            database = json.load(jfile)
    except FileNotFoundError:
        msg = '* ERROR: {} calibration database not found'.format(databasefile)
        raise SystemError(msg)

    msg = '\nCalibration database set to {}'.format(databasefile)
    logfile.print(msg)

    # check that the requested calibration is available in the calibration
    # database
    if redustep not in database:
        msg = '* ERROR: {} calibration not available in database file {}'.format(redustep, databasefile)
        raise SystemError(msg)

    # generate expected signature for calibration image
    sortedkeys = database['signaturekeys']
    expected_signature = dict()
    for keyword in sortedkeys:
        if keyword not in signature:
            msg = '* ERROR: keyword {} not present in {} calibration'.format(keyword, redustep)
            raise SystemError(msg)
        expected_signature[keyword] = signature[keyword]
    ssig = signature_string(sortedkeys, expected_signature)

    # check that the calibration key is available in the main database
    if ssig in database[redustep]:
        msg = '-> looking for calibration {} with signature {}'.format(redustep, ssig)
        logfile.print(msg)
        mjdobsarray_str = np.array([strmjd for strmjd in database[redustep][ssig].keys()])
        mjdobsarray_float = np.array([float(strmjd) for strmjd in database[redustep][ssig].keys()])
        ipos = find_nearest(mjdobsarray_float, mjdobs)
        mjdkey = mjdobsarray_str[ipos]
        delta_mjd = float(mjdkey) - mjdobs
        logfile.print('->   mjdobsarray.......: {}'.format(mjdobsarray_float))
        logfile.print('->   looking for mjdobs: {}'.format(mjdobs))
        logfile.print('->   nearest value is..: {}'.format(mjdkey))
        logfile.print('->   delta_mjd (days)..: {}'.format(delta_mjd))
        calfname = database[redustep][ssig][mjdkey]['fname']
        with fits.open(calfname) as hdul:
            image2d_cal = hdul[0].data
        ierr = 0
    else:
        logfile.print('* WARNING: signature {} not found for {} image'.format(ssig, redustep))
        ierr = 1
        if redustep == 'bias':
            if naxis1_ is not None and naxis2_ is not None:
                image2d_cal = np.ones((naxis2_, naxis1_), dtype=float)
                delta_mjd, closestbias = findclosestquant(mjdobs, database[redustep], 'QUANT500')
                logfile.print('->   looking for mjdobs: {}'.format(mjdobs))
                logfile.print('->   delta_mjd (days)..: {}'.format(delta_mjd))
                logfile.print('->   Using median value of closest bias frame: {}'.format(closestbias))
                image2d_cal *= closestbias
                calfname = 'None (closest bias with different signature)'
                return ierr, delta_mjd, image2d_cal, calfname
        elif redustep == 'flat-imaging':
            if naxis1_ is not None and naxis2_ is not None:
                delta_mjd = 0.0
                logfile.print('->   looking for mjdobs: {}'.format(mjdobs))
                logfile.print('->   Using dummy flat of ones')
                image2d_cal = np.ones((naxis2_, naxis1_), dtype=float)
                calfname = 'None (flat image with ones)'
                return ierr, delta_mjd, image2d_cal, calfname
        raise SystemError('No alternative implemented in this case!')

    # double check
    naxis2, naxis1 = image2d_cal.shape
    if naxis1_ is not None:
        if naxis1 != naxis1_:
            msg = '* ERROR: NAXIS1 does not match: {} vs. {}'.format(naxis1, naxis1_)
            raise SystemError(msg)
    if naxis2_ is not None:
        if naxis2 != naxis2_:
            msg = '* ERROR: NAXIS2 does not match: {} vs. {}'.format(naxis2, naxis2_)
            raise SystemError(msg)

    return ierr, delta_mjd, image2d_cal, calfname
