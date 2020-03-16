# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#


def check_list_filter(filterexpression, storedkeywords, debug=False):
    """
    Evaluate filter expression based on stored keywords

    Parameters
    ----------
    filterexpression : str
        Logical expression involving keywords to be evaluated in order to
        filter the generated list.
    storedkeywords : dict
        Dictionary containing the values of the relevant keywords.
    debug : bool
        If True, display expression to be evaluated.

    Returns
    -------
    result : bool
        Result of evaluating the logical expression.
    """

    # Replace k[<keyword] by actual keyword value
    i = 0
    s = ''
    while True:
        j = filterexpression[i:].find('k[')
        if j < 0:
            s += filterexpression[i:]
            break
        s += filterexpression[i:(i+j)]
        jj = filterexpression[(i+j):].find(']')
        if jj < 0:
            s += filterexpression[i:]
            break
        kwd = filterexpression[(i+j+2):(i+j+jj)].upper()
        s += str(storedkeywords[kwd])
        i += j + jj + 1

    if debug:
        print('Expression to be evaluated: {}'.format(s))

    try:
        result = eval(s)
    except (NameError, ValueError, SyntaxError):
        msg = 'ERROR: while evaluating {}'.format(s)
        raise SystemError(msg)

    return result
