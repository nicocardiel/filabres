# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .version import version
__version__ = version

# requirement operators (using the logical operators syntax from Fortran77)
REQ_OPERATORS = {
    '.NE.': '!=',
    '.GT.': '>',
    '.GE.': '>=',
    '.LT.': '<',
    '.LE.': '<='
}

LISTDIR = './lists/'
