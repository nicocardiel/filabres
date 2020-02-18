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


def retrieve_calibration(instrument, redustep, signature, mjdobs, verbose=False):
    """
    Retrieve calibration from main database.

    Parameters
    ==========
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
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    image2d_cal : numpy 2D array
        Numpy array with the calibration data.
    calfilename: str
        Calibration file name
    """

    calfilename = None

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
        print('\nMain database set to {}'.format(databasefile))

    # check that the requested calibration is available in the calibration
    # database
    if redustep not in database:
        msg = '* ERROR: {} calibration not available in database ' \
              'file {}'.format(redustep, databasefile)
        raise SystemError(msg)

    # generate expected signature for calibration image
    sortedkeys = database['sortedkeys']
    expected_signature = dict()
    for keyword in sortedkeys:
        if keyword not in signature:
            msg = '* ERROR: keyword {} not present in {} calibration'.format(
                  keyword, redustep)
            raise SystemError(msg)
        expected_signature[keyword] = signature[keyword]
    sortedkeys_, key = signature_string(expected_signature)

    # check that the calibration key is available in the main database
    if key in database[redustep]:
        if verbose:
            print('-> looking for calibration {} with signature {}'.format(
                redustep, key))
        mjdobsarray_str = np.array([strmjd for strmjd in
                                   database[redustep][key].keys()])
        mjdobsarray_float = np.array([float(strmjd) for strmjd in
                                      database[redustep][key].keys()])
        if verbose:
            print('->   mjdobsarray:', mjdobsarray_float)
            print('->   mjdobs.....:', mjdobs)
        ipos = find_nearest(mjdobsarray_float, mjdobs)
        mjdkey = mjdobsarray_str[ipos]
        calfilename = database[redustep][key][mjdkey]['filename']
        with fits.open(calfilename) as hdul:
            image2d_cal = hdul[0].data
    else:
        print('* WARNING: signature {} not found in main database'.format(key))
        return None, None

    # double check
    naxis2, naxis1 = image2d_cal.shape
    if 'NAXIS1' in signature:
        naxis1_ = signature['NAXIS1']
        if naxis1 != signature['NAXIS1']:
            msg = '* ERROR: NAXIS1 does not match: {} vs. {}'.format(
                  naxis1, naxis1_)
            raise SystemError(msg)
    if 'NAXIS2' in signature:
        naxis2_ = signature['NAXIS2']
        if naxis2 != signature['NAXIS2']:
            msg = '* ERROR: NAXIS2 does not match: {} vs. {}'.format(
                  naxis2, naxis2_)
            raise SystemError(msg)

    return image2d_cal, calfilename
