import numpy as np


def statsumm(image2d, rm_nan=False, verbose=False):
    """
    Compute statistical summary of 2D image.

    Note that the results are stored as native integers and float
    to avoid problems when saving the dictionary as a JSON file
    (that does not admit np.int nor np.float objects).

    Parameters
    ==========
    image2d : numpy 2D array
        Array with input image.
    rm_nan : bool
        If True, filter out NaN values before computing statistics.
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    output : dict
        Statistical summary in dictionary form.
    """

    x = image2d.flatten()
    if rm_nan:
        x = x[np.logical_not(np.isnan(x))]
    npoints = len(x)
    ok = npoints > 0
    quant025 = float(np.percentile(x, 2.5)) if ok else 0
    quant159 = float(np.percentile(x, 15.9)) if ok else 0
    quant250 = float(np.percentile(x, 25.0)) if ok else 0
    quant500 = float(np.percentile(x, 50.0)) if ok else 0
    quant750 = float(np.percentile(x, 75.0)) if ok else 0
    quant841 = float(np.percentile(x, 84.1)) if ok else 0
    quant975 = float(np.percentile(x, 97.5)) if ok else 0
    sigmag = 0.7413 * (quant750 - quant250)
    result = {
        'NPOINTS': npoints,
        'MINIMUM': float(np.min(x)) if ok else 0,
        'QUANT025': quant025,
        'QUANT159': quant159,
        'QUANT250': quant250,
        'QUANT500': quant500,
        'QUANT750': quant750,
        'QUANT841': quant841,
        'QUANT975': quant975,
        'MAXIMUM': float(np.max(x)) if ok else 0,
        'ROBUSTSTD': sigmag,
    }

    if verbose:
        print(result)

    return result
