import pkgutil
from six import StringIO
import yaml

from filabres import REQ_OPERATORS

def load_instrument_configuration(instrument, redustep, verbose=False):
    """
    Load instrument configuration from YAML file.

    Parameters
    ----------
    instrument : str or None
        Instrument-obsmode string identifying the instrument
        and observing mode. If None, a list with the available
        instruments and reduction steps is displayed.
    redustep : str or None
        Reduction step. If None, a list with the available
        instruments and reduction steps is displayed.
    verbose : bool
        If True, display intermediate information.

    Returns
    -------
    instconf : dict
        Instrument configuration. See file configuration.yaml
        for details.
    """

    # load configuration file
    dumdata = pkgutil.get_data('filabres.instrument', 'configuration.yaml')
    dumfile = StringIO(dumdata.decode('utf8'))
    bigdict = yaml.load(dumfile)

    # check instrument and reduction step
    available_instruments = list(bigdict.keys())
    if instrument not in available_instruments:
        if instrument is not None:
            print('ERROR: invalid instrument: {}'.format(instrument))
        print('Avaliable options are:')
        for instrument_ in available_instruments:
            print('-i/--instrument {}'.format(instrument_))
        raise SystemExit()
    else:
        # check reduction step
        available_redusteps = ['initialize']
        available_redusteps += list(bigdict[instrument]['imagetypes'])
        if redustep not in available_redusteps:
            if redustep is not None:
                print('ERROR: invalid reduction step: {}'.format(redustep))
            print('Avaliable options are:')
            for redustep_ in available_redusteps:
                print('-rs/--reduction_step {}'.format(redustep_))
            raise SystemExit()

    # define instrument configuration dictionary
    instconf = bigdict[instrument]

    # check that the keywords of the requirements and the signature of the
    # different image types are all included in the masterkeywords list
    for imagetype in instconf['imagetypes']:
        # check keywords in requirements
        for keyword in instconf['imagetypes'][imagetype]['requirements']:
            for operator in REQ_OPERATORS:
                lenop = len(operator)
                if keyword[-lenop:] == operator:
                    keyword = keyword[:-lenop]
                    break
            if keyword not in instconf['masterkeywords']:
                print('ERROR in configuration.yaml file')
                print('-> the (requirements) keyword {} is not included in '
                      'the masterkeywords list'.format(keyword))
                raise SystemExit()

        # check keywords in signature
        for keyword in instconf['imagetypes'][imagetype]['signature']:
            if keyword not in instconf['masterkeywords']:
                print('ERROR in configuration.yaml file')
                print('-> the (signature) keyword {} is not included in '
                      'the masterkeywords list'.format(keyword))
                raise SystemExit()

    if verbose:
        print('* Instrument configuration: {}'.format(instconf))

    return instconf
