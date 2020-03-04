# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

def check_tslash(dir):
    """Auxiliary function to add trailing slash when not present"""
    if dir[-1] != '/':
        dir += '/'
    return dir