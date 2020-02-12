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


def signature_string(signature):
    """
    Return signature string.

    Parameters
    ==========
    signature : dict
        Signature dictionary. Note that the keywords are not expected
        to be sorted.

    Returns
    =======
    sortedkeys : list
        List of signature keys in alphabetic order.
    output : str
        String sequence with the values of the different signature
        keywords in alphabetic order.
    """

    sortedkeys = list(signature.keys())
    sortedkeys.sort()
    output = ''
    for i, key in enumerate(sortedkeys):
        if i != 0:
            output += '__'
        output += str(signature[key])
    return sortedkeys, output
