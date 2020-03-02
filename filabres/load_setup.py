import yaml


def load_setup(setupfile, verbose=False):
    """
    Load setup file

    Parameters
    ==========
    setupfile : str or None
        Setup file name.
    verbose : bool
        If True, display intermediate information.

    Returns
    =======
    instrument : str
        Instrument name.
    datadir : str
        Data directory where the original FITS files are stored.
    """

    if setupfile is None:
        setupfile = 'setup_filabres.yaml'
    with open(setupfile) as yamlfile:
        setupdata = yaml.load(yamlfile, Loader=yaml.Full)

    instrument = setupdata['instrument']
    datadir = setupdata['datadir']

    if verbose:
        print('* Instrument: {}'.format(instrument))
        print('* Datadir: {}'.format(datadir))

    return instrument, datadir
