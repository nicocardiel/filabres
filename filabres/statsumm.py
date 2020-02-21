import numpy as np


def statsumm(image2d, header=None, redustep=None, rm_nan=False, verbose=False):
    """
    Compute statistical summary of 2D image.

    Note that the results are stored as native integers and float
    to avoid problems when saving the dictionary as a JSON file
    (that does not admit np.int nor np.float objects).

    Parameters
    ==========
    image2d : numpy 2D array or None
        Array with input image.
    header : astropy header or None
        Header to be updated
    redustep : str
        Reduction step.
    rm_nan : bool
        If True, filter out NaN values before computing statistics.
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    output : dict
        Statistical summary in dictionary form.
    """

    if image2d is None:
        x = np.array([], dtype=np.float)
        npoints = 0
    else:
        x = image2d.flatten()
        npoints = len(x)
    if rm_nan:
        x = x[np.logical_not(np.isnan(x))]
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

    if header is not None:
        header.add_history('Statistical analysis of combined {} image:'.format(redustep))
        for key in result:
            header.add_history(' - {}: {}'.format(key, result[key]))

    return result
