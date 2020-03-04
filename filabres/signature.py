# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

"""
Auxiliary functions to handle image signatures.
"""


def getkey_from_signature(signature, key):
    """
    Return key from signature

    Parameters
    ==========
    signature: dictionary
        Python dictionary storing the signature keywords.
    key : str
        Keyword to be obtained from signature
    """
    if key not in signature:
        print('* ERROR: {} not found in signature'.format(key))
        raise SystemExit()
    else:
        return signature[key]


def signature_string(signaturekeys, signature):
    """
    Return signature string.

    Parameters
    ==========
    signaturekeys : list
        Sorted list of keywords.
    signature : dict
        Signature dictionary. Note that the keywords are not expected
        to be sorted.

    Returns
    =======
    output : str
        String sequence with the values of the different signature
        keywords, preserving .
    """

    output = ''
    for i, key in enumerate(signaturekeys):
        if i != 0:
            output += '__'
        output += str(signature[key])
    return output
