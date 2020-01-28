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
    instconf = yaml.load(dumfile)

    # determine available instruments
    list_available = list(instconf.keys())
    list_available.remove('default')

    # check instrument
    if instrument in list_available:
        print(instconf[instrument])
    else:
        raise ValueError('Unexpected instrument')

    return instconf
