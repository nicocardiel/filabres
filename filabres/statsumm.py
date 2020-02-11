import numpy as np


def statsumm(image2d, rm_nan=False, verbose=False):
    """
    Compute statistical summary of 2D image

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
    q15 = float(np.percentile(x, 15.86553)) if ok else 0
    q25 = float(np.percentile(x, 25)) if ok else 0
    q50 = float(np.percentile(x, 50)) if ok else 0
    q75 = float(np.percentile(x, 75)) if ok else 0
    q84 = float(np.percentile(x, 84.13447)) if ok else 0
    sigmag = 0.7413 * (q75 - q25)
    result = {
        'npoints': npoints,
        'minimum': float(np.min(x)) if ok else 0,
        'percentile25': q25,
        'median': q50,
        'mean': float(np.mean(x)) if ok else 0,
        'percentile75': q75,
        'maximum': float(np.max(x)) if ok else 0,
        'std': float(np.std(x)) if ok else 0,
        'robust_std': sigmag,
        'percentile15': q15,
        'percentile84': q84
    }

    if verbose:
        print(result)

    return result
