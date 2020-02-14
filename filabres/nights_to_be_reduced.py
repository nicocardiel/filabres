import fnmatch
import os

from filabres import DATADIR

def nights_to_be_reduced(args_night, verbose=False, debug=False):
    """Generate list of nights to be reduced.

    Parameters
    ----------
    args_night : str or None
        Night label. Wildcards are valid. If None, all the nights
        within the DATADIR directory are considered.
    verbose : bool
        If True, display intermediate information.
    debug : bool
        If True, display additional debugging information

    Returns
    -------
    list_of_nights : list
        List of nights matching the selection filter.

    """

    if args_night is None:
        night = '*'
    else:
        night = args_night

    try:
        all_nights = os.listdir(DATADIR)
    except FileNotFoundError:
        print('ERROR: directory {} not found'.format(DATADIR))
        raise SystemExit()

    list_of_nights = [filename for filename in all_nights
                      if fnmatch.fnmatch(filename, night)]

    if len(list_of_nights) == 0:
        print('ERROR: no subdirectory matches the night selection')
        raise SystemExit()

    list_of_nights.sort()

    print('* Number of nights found: {}'.format(len(list_of_nights)))
    if verbose:
        if debug:
            print('* List of nights: {}'.format(list_of_nights))

    return list_of_nights
