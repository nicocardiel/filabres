# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import os

from .pause_debugplot import pause_debugplot
from .statsumm import statsumm
from .ximshow import ximshow

NMAXGAIA = 2000


class AstrSummary(object):
    """
    Store relevant information concerning the astrometric calibration.

    Parameters
    ----------
    pixscale : float
        Pixel scale (in arcsec/pixel).
    ntargets : int
        Number of targets.
    meanerr : float
        Mean error (in arcseconds).

    Attributes
    ----------
    pixscale : float
        Pixel scale (in arcsec/pixel).
    ntargets : int
        Number of targets.
    meanerr : float
        Mean error (in arcseconds).

    """
    def __init__(self, pixscale, ntargets, meanerr):
        self.pixscale = pixscale
        self.ntargets = ntargets
        self.meanerr = meanerr


def plot_astrometry(output_fname, image2d, mask2d,
                    peak_x, peak_y, pred_x, pred_y, xcatag, ycatag,
                    pixel_scales_arcsec_pix, workdir, interactive, logfile,
                    suffix):
    """
    Generate plots with the results of the astrometric calibration.

    Parameters
    ----------
    output_fname : str or None
        Output file name.
    image2d : numpy 2D array
        Image to be calibrated.
    mask2d : numpy 2D array
        Useful region mask.
    peak_x : numpy 1D array
        Measured X coordinate of the detected objects.
    peak_y : numpy 1D array
        Measured Y coordinate of the detected objects.
    pred_x : numpy 1D array
        X coordinate of the detected objects predicted by the
        astrometric calibration.
    pred_y : numpy 1D array
        X coordinate of the detected objects predicted by the
        astrometric calibration.
    xcatag : numpy 1D array
        X coordinate of the full catalog of objects as
        predicted by the astrometric calibration.
    ycatag : numpy 1D array
        X coordinate of the full catalog of objects as
        predicted by the astrometric calibration.
    pixel_scales_arcsec_pix : numpy 1D array
        X and Y pixel scales, in arcsec/pix.
    workdir : str
        Work subdirectory.
    interactive : bool or None
        If True, enable interactive execution (e.g. plots,...).
    logfile : ToLogFile instance
        Log file where the astrometric calibration information is
        stored.
    suffix : str
        Suffix to be appended to PDF output.

    Returns
    -------
    astrsumm : instance of AstrSumm
        Summary of astrometric calibration.

    """

    ntargets = len(peak_x)
    naxis2, naxis1 = image2d.shape

    mean_pixel_scale_arcsec_pix = float(np.mean(pixel_scales_arcsec_pix))
    delta_x = (pred_x - peak_x) * mean_pixel_scale_arcsec_pix
    delta_y = (pred_y - peak_y) * mean_pixel_scale_arcsec_pix
    delta_r = np.sqrt(delta_x * delta_x + delta_y * delta_y)
    rorder = np.argsort(delta_r)
    meanerr = float(np.mean(delta_r))
    logfile.print('astrometry-{}> Number of targest found: {}'.format(suffix, ntargets))
    logfile.print('astrometry-{}> Mean error (arcsec)....: {}'.format(suffix, meanerr))
    for i, iorder in enumerate(rorder):
        if delta_r[iorder] > 3 * meanerr:
            logfile.print('-> outlier point #{}, delta_r (arcsec): {}'.format(i+1, delta_r[iorder]))

    plot_suptitle = '[File: {}]'.format(os.path.basename(output_fname))
    plot_title = 'astrometry-{} (npoints={}, meanerr={:.3f} arcsec)'.format(suffix, ntargets, meanerr)
    # plot 1: X and Y errors
    pp = PdfPages('{}/astrometry-{}.pdf'.format(workdir, suffix))
    fig, ax = plt.subplots(1, 1, figsize=(11.7, 8.3))
    fig.suptitle(plot_suptitle)
    ax.plot(delta_x, delta_y, 'mo', alpha=0.5)
    rmax = 2.0  # arcsec
    for i, iorder in enumerate(rorder):
        if abs(delta_x[iorder]) < rmax and abs(delta_y[iorder]) < rmax:
            ax.text(delta_x[iorder], delta_y[iorder], str(i+1), fontsize=15)
    circle1 = plt.Circle((0, 0), 0.5, color='b', fill=False)
    circle2 = plt.Circle((0, 0), 1.0, color='g', fill=False)
    circle3 = plt.Circle((0, 0), 1.5, color='r', fill=False)
    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(circle3)
    ax.set_xlim([-rmax, rmax])
    ax.set_ylim([-rmax, rmax])
    ax.set_xlabel('delta X (arcsec): predicted - peak')
    ax.set_ylabel('delta Y (arcsec): predicted - peak')
    ax.set_title(plot_title)
    ax.set_aspect('equal', 'box')
    pp.savefig()
    if interactive:
        plt.show()
    # plots 2 and 3: histograms with deviations in the X and Y axis
    for iplot in [1, 2]:
        fig, ax = plt.subplots(1, 1, figsize=(11.7, 8.3))
        fig.suptitle(plot_suptitle)
        if iplot == 1:
            ax.hist(delta_x, 30)
            ax.set_xlabel('delta X (arcsec): predicted - peak')
        else:
            ax.hist(delta_y, 30)
            ax.set_xlabel('delta Y (arcsec): predicted - peak')
        ax.set_ylabel('Number of targets')
        ax.set_title(plot_title)
        pp.savefig()
        if interactive:
            plt.show()
    # plot 3: image with identified objects
    stdum = statsumm(image2d=image2d, mask2d=mask2d, rm_nan=True)
    z1 = stdum['QUANT500'] - 1 * stdum['ROBUSTSTD']
    z2 = stdum['QUANT500'] + 10 * stdum['ROBUSTSTD']
    ax = ximshow(image2d, cmap='gray_r', show=False, z1z2=(z1, z2),
                 geometry=None, figuredict={'figsize': (11.7, 8.3)},
                 title=plot_title, tight_layout=False)
    ax.plot(peak_x, peak_y, 'bo', fillstyle='none', markersize=10, label='peaks')
    for i, iorder in enumerate(rorder):
        ax.text(peak_x[iorder], peak_y[iorder], str(i + 1), fontsize=15, color='blue')
    ax.plot(xcatag, ycatag, 'mo', alpha=0.5, markersize=10, fillstyle='none', label='predicted GaiaDR2')
    ax.plot(pred_x, pred_y, 'g+', markersize=10, label='predicted peaks')
    # ax.set_xlim([min(np.min(xcatag), -0.5), max(np.max(xcatag), naxis1 + 0.5)])
    ax.set_xlim([-0.05 * naxis1, 1.05 * naxis1])
    # ax.set_ylim([min(np.min(ycatag), -0.5), max(np.max(ycatag), naxis2 + 0.5)])
    ax.set_ylim([-0.05 * naxis2, 1.05 * naxis2])
    ax.legend()
    plt.suptitle(plot_suptitle)
    pp.savefig()
    if interactive:
        pause_debugplot(debugplot=12, pltshow=True, tight_layout=False)
    pp.close()
    plt.close()

    astrsumm = AstrSummary(mean_pixel_scale_arcsec_pix, ntargets, meanerr)
    return astrsumm
