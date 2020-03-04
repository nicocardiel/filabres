# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})  # avoid warning


def set_window_geometry(geometry):
    """Set window geometry.

    Parameters
    ==========
    geometry : tuple (4 integers) or None
        x, y, dx, dy values employed to set the Qt backend geometry.

    """

    if geometry is not None:
        x_geom, y_geom, dx_geom, dy_geom = geometry
        mngr = plt.get_current_fig_manager()
        if 'window' in dir(mngr):
            try:
                mngr.window.setGeometry(x_geom, y_geom, dx_geom, dy_geom)
            except AttributeError:
                pass
            else:
                pass
