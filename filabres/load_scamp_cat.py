import numpy as np


def load_scamp_cat(catalogue, workdir, verbose):
    """
    Load X, Y coordinates from catalogue generated with SCAMP

    Parameters
    ==========
    catalogue : str
        Catalogue to be read. It must be 'full' or 'merged'.
    workdir : str
        Work subdirectory.
    verbose : bool or None
        If True, display intermediate information.

    Returns
    =======
    col1, col2 : numpy 1D arrays
        X, Y coordinates of the peaks (only if catalogue is 'full').
        RA, DEC coordinates of the peaks (only if catalogue is 'merged').
    """

    if catalogue not in ['full', 'merged']:
        msg = 'Invalid catalogue description: {}'.format(catalogue)
        raise SystemError(msg)

    filename = '{}/{}_1.cat'.format(workdir, catalogue)
    with open(filename, 'rt') as f:
        fulltxt = f.readlines()

    if verbose:
        print('Reading {}'.format(filename))

    # determine relevant column numbers
    if catalogue == 'full':
        colnames = ['X_IMAGE', 'Y_IMAGE', 'CATALOG_NUMBER']
    else:
        colnames = ['ALPHA_J2000', 'DELTA_J2000']
    ncol = []
    for col in colnames:
        ii = None
        for i, line in enumerate(fulltxt):
            if col in line:
                ii = i + 1
                break
        if ii is None:
            msg = '{} not found in {}'.format(col, filename)
            raise SystemError(msg)
        if verbose:
            print('{} is located in column #{}'.format(col, ii))
        ncol.append(ii - 1)

    # read full data set
    fulltable = np.genfromtxt(filename)

    if catalogue == 'full':
        # delete invalid rows (those with CATALOG_NUMBER == 0)
        valid_rows = np.where(fulltable[:, ncol[2]] != 0)[0]
        if verbose:
            print('Number of objects read: {}'.format(len(valid_rows)))
        newtable = fulltable[valid_rows, :]
    else:
        newtable = fulltable

    col1 = newtable[:, ncol[0]]
    col2 = newtable[:, ncol[1]]

    return col1, col2
