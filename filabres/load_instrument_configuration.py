import pkgutil
from six import StringIO
import yaml


def load_instrument_configuration(instrument):
    """Load instrument configuration from YAML file.

    Parameters
    ----------
    instrument : str
        Instrument-obsmode string identifying the instrument
        and observing mode.

    Returns
    -------
    instconf : dictionary
        Available instrument configurations.

    """

    # load configuration file
    dumdata = pkgutil.get_data(
        'filabres.instrument',
        'instrument_definition.yaml'
    )
    dumfile = StringIO(dumdata.decode('utf8'))
    bigdict = yaml.load(dumfile)

    # determine available instruments
    list_available = list(bigdict.keys())
    list_available.remove('default')

    # check instrument
    if instrument not in list_available:
        raise ValueError('Unexpected instrument')

    # append default keywords
    instconf = bigdict[instrument]
    print(instconf)
    instconf['keywords'] = bigdict['default']['keywords'] + \
        instconf['keywords']
    print(instconf)

    return instconf
