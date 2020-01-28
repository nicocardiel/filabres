import pkgutil
from six import StringIO
import yaml


def load_instrument_configuration(instrument):
    """Load instrument configuration from YAML file.

    Parameters
    ----------
    instrument : str or None
        Instrument-obsmode string identifying the instrument
        and observing mode. If None, a list with the available
        instruments is displayed.

    Returns
    -------
    instconf : dictionary
        Available instrument configurations.

    """

    # load configuration file
    dumdata = pkgutil.get_data('filabres.instrument', 'configuration.yaml')
    dumfile = StringIO(dumdata.decode('utf8'))
    bigdict = yaml.load(dumfile)

    # determine available instruments
    list_available = list(bigdict.keys())
    list_available.remove('default')

    # check instrument
    if instrument not in list_available:
        if instrument is not None:
            print('ERROR: invalid instrument')
        for dumid in list_available:
            print('Available instruments:')
            print('- {}'.format(dumid))
        raise SystemExit()

    # append default keywords
    instconf = bigdict[instrument]
    instconf['keywords'] = bigdict['default']['keywords'] + \
        instconf['keywords']

    return instconf
