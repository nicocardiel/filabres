from scipy.signal import medfilt2d


def maskfromflat(image2d_flat, kernel_size=11, threshold=0.3):
    """
    Generate mask from flatfield.

    Parameters
    ==========
    image2d_flat : numpy 2d array
        Flatfield image.
    kernel_size : int
        Size of the median filter window (should be odd).
    threshold : float
        Pixels below 'threshold' are set to 0.0. Pixels above
        this value are set to 1.0.

    Returns
    =======
    mask2d : numpy 2d array
        Mask corresponding to useful region.
    """

    mask2d = medfilt2d(image2d_flat, kernel_size=kernel_size)
    mask2d[mask2d < threshold] = 0.0
    mask2d[mask2d > 0.9 * threshold] = 1.0
    return mask2d
