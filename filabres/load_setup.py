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
    image_corrections_file : str
        Name of the file containing the image corrections.
    """

    if setupfile is None:
        setupfile = 'setup_filabres.yaml'
    with open(setupfile) as yamlfile:
        setupdata = yaml.load(yamlfile)

    for kwd in ['instrument', 'datadir', 'image_corrections_file']:
        if kwd not in setupdata:
            msg = 'Expected keyword {} missing in {}'.format(kwd, setupfile)
            raise SystemError(msg)

    instrument = setupdata['instrument']
    datadir = setupdata['datadir']
    image_corrections_file = setupdata['image_corrections_file']

    if verbose:
        print('* instrument: {}'.format(instrument))
        print('* datadir: {}'.format(datadir))
        print('* image_corrections: {}'.format(image_corrections_file))

    return instrument, datadir, image_corrections_file
