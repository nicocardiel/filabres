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
    """
    result = None
    delta_mjdobs = None
    for ssig in database.keys():
        for smjd in database[ssig].keys():
            mjdobs_ = float(smjd)
            if result is None:
                delta_mjdobs = abs(mjdobs - mjdobs_)
                result = database[ssig][smjd]['statsumm'][quantile]
            else:
                if abs(mjdobs - mjdobs_) < delta_mjdobs:
                    delta_mjdobs = abs(mjdobs - mjdobs_)
                    result = database[ssig][smjd]['statsumm'][quantile]
    return result


def retrieve_calibration(instrument, redustep, signaturekeys, signature, mjdobs,
                         verbose=False):
    """
    Retrieve calibration from main database.

    Parameters
    ==========
    instrument : string
        Instrument name.
    redustep : string
        Reduction step.
    signaturekeys : list()
        Signature keywords.
    signature : dict()
        Signature of the image to be calibrated. The selected
        calibration must have the expected signature.
    mjdobs: float
        Modified Julian Date, use to locate the closest calibration
        available in the main database.
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    ierr : int
        Error status value. 0: no error. 1: calibration not found.
    image2d_cal : numpy 2D array
        Numpy array with the calibration data.
    calfilename: str
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
    if verbose:
        print('\nCalibration database set to {}'.format(databasefile))

    # check that the requested calibration is available in the calibration
    # database
    if redustep not in database:
        msg = '* ERROR: {} calibration not available in database file {}'.format(redustep, databasefile)
        raise SystemError(msg)

    # generate expected signature for calibration image
    sortedkeys = database['sortedkeys']
    expected_signature = dict()
    for keyword in sortedkeys:
        if keyword not in signature:
            msg = '* ERROR: keyword {} not present in {} calibration'.format(keyword, redustep)
            raise SystemError(msg)
        expected_signature[keyword] = signature[keyword]
    ssig = signature_string(signaturekeys, expected_signature)

    # check that the calibration key is available in the main database
    if ssig in database[redustep]:
        if verbose:
            print('-> looking for calibration {} with signature {}'.format(
                redustep, ssig))
        mjdobsarray_str = np.array([strmjd for strmjd in database[redustep][ssig].keys()])
        mjdobsarray_float = np.array([float(strmjd) for strmjd in database[redustep][ssig].keys()])
        if verbose:
            print('->   mjdobsarray:', mjdobsarray_float)
            print('->   mjdobs.....:', mjdobs)
        ipos = find_nearest(mjdobsarray_float, mjdobs)
        mjdkey = mjdobsarray_str[ipos]
        calfilename = database[redustep][ssig][mjdkey]['filename']
        with fits.open(calfilename) as hdul:
            image2d_cal = hdul[0].data
        ierr = 0
    else:
        print('* WARNING: signature {} not found for {} image'.format(ssig, redustep))
        ierr = 1
        if redustep == 'bias':
            if naxis1_ is not None and naxis2_ is not None:
                image2d_cal = np.ones((naxis2_, naxis1_), dtype=np.float)
                closestbias = findclosestquant(mjdobs, database[redustep], 'QUANT500')
                image2d_cal *= closestbias
                calfilename = 'None (closest bias with different signature)'
                return ierr, image2d_cal, calfilename
        elif redustep == 'flat-imaging':
            if naxis1_ is not None and naxis2_ is not None:
                image2d_cal = np.ones((naxis2_, naxis1_), dtype=np.float)
                calfilename = 'None (flat image with ones)'
                return ierr, image2d_cal, calfilename
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

    return ierr, image2d_cal, calfilename
