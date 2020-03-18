# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#


def check_list_mode(list_mode, args_keyword, args_keyword_sort, args_plotxy, args_plotimage, args_ndecimal):
    """
    Check compatibility of list_mode with some conflicting arguments.

    Parameters
    ----------
    list_mode : str
        List mode:
        - long: each file in a single line with additional keywords
        - basic: each file in a single line without the file path and
                 without additional keywords
        - singleline: all the files in a single line without additional keywords
    args_keyword : list or None
        List with additional keywords to be displayed when img2
        is not None (otherwise an error is raised). Note that each
        value in this list is also a list (with a single keyword).
    args_keyword_sort : list or None
        List with keywords to be used to sort the displayed table.
        If not given in args_keyword, the keywords will be appended
        to the list of displayed keywords.
    args_plotxy : bool
        If True, plot scatter matrices to visualize trends in the
        selected keywords.
    args_plotimage : bool
        If True, display selected images.
    args_ndecimal : int
        Number of decimal places for floats.
    """

    if list_mode in ["basic", "singleline"]:
        msg = ''
        if args_keyword is not None:
            msg += 'WARNING: -k KEYWORD is ignored with --list_mode {}'.format(list_mode)
        if args_keyword_sort is not None:
            if msg != '':
                msg += '\n'
            msg += 'WARNING: -ks KEYWORD is ignored with --list_mode {}'.format(list_mode)
        if args_plotxy:
            if msg != '':
                msg += '\n'
            msg += 'WARNING: -pxy is ignored with --list_mode {}'.format(list_mode)
        if args_plotimage:
            if msg != '':
                msg += '\n'
            msg += 'WARNING: -pi is ignored with --list_mode {}'.format(list_mode)
        if args_ndecimal:
            if msg != '':
                msg += '\n'
            msg += 'WARNING: -nd INTEGER is ignored with --list_mode {}'.format(list_mode)
        if msg != '':
            print(msg)
