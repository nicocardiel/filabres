# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from scipy.signal import medfilt2d
from scipy.ndimage import gaussian_filter


def maskfromflat(image2d_flat, kernel_size=11, threshold=0.5):
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

    # median filter to remove isolated bad pixels
    mask2d = medfilt2d(image2d_flat, kernel_size=kernel_size)
    # set mask according to threshold
    mask2d[mask2d < threshold] = 0.0
    mask2d[mask2d > 0.9 * threshold] = 1.0
    # enlarge the masked region
    mask2d = gaussian_filter(mask2d, sigma=5)
    mask2d[mask2d < 0.99] = 0.0
    # return result
    return mask2d
