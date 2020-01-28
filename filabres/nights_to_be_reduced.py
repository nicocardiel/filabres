import fnmatch
import os

def nights_to_be_reduced(datadir, args_night, verbose=False):
    """Generate list of nights to be reduced.

    Parameters
    ----------
    datadir : str
        Data directory containing the different nights to be reduced.
    args_night : str or None
        Night label. Wildcards are valid. If None, all the nights
        within the 'datadir' directory are considered.
    verbose : bool
        If True, display intermediate information.

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
        all_nights = os.listdir(datadir)
    except FileNotFoundError:
        print('ERROR: invalid --datadir value')
        raise SystemExit()

    list_of_nights = [filename for filename in all_nights
                      if fnmatch.fnmatch(filename, night)]

    if len(list_of_nights) == 0:
        print('ERROR: no subdirectory matches the night selection')
        raise SystemExit()

    if verbose:
        print('* List of nights: {}'.format(list_of_nights))

    return list_of_nights
