import pkgutil
from six import StringIO
import yaml

from .statsumm import statsumm

from filabres import REQ_OPERATORS


def load_instrument_configuration(instrument, redustep,
                                  dontcheckredustep=False,
                                  verbose=False, debug=False):
    """
    Load instrument configuration from YAML file.

    Parameters
    ----------
    instrument : str
        Instrument name.
    redustep : str or None
        Reduction step. If None, and 'checkonlyredustep' is False,
        a list with the available reduction steps is displayed.
    dontcheckredustep : bool
        If True, do not check 'redustep'.
    verbose : bool
        If True, display intermediate information.
    debug : bool
        If True, display additional debugging information.

    Returns
    -------
    instconf : dict
        Instrument configuration. See file configuration.yaml
        for details.
    """

    # load configuration file
    if verbose:
        print('* Loading instrument configuration')
    dumdata = pkgutil.get_data('filabres.instrument', 'configuration.yaml')
    dumfile = StringIO(dumdata.decode('utf8'))
    bigdict = yaml.load(dumfile)

    # check instrument and reduction step
    available_instruments = list(bigdict.keys())
    if instrument not in available_instruments:
        if instrument is None:
            print('ERROR: missing instrument!')
        else:
            print('ERROR: invalid instrument: {}'.format(instrument))
        print('Possible options:')
        for instrument_ in available_instruments:
            print(' - {}'.format(instrument_))
        raise SystemExit()
    else:
        if not dontcheckredustep:
            # check reduction step
            defined_redusteps = {'initialize': True}
            for img in bigdict[instrument]['imagetypes']:
                defined_redusteps[img] = bigdict[instrument]['imagetypes'][img]['executable']
            redustep_is_ok = True
            if redustep not in defined_redusteps:
                redustep_is_ok = False
            else:
                if not defined_redusteps[redustep]:
                    redustep_is_ok = False
            if not redustep_is_ok:
                if redustep is None:
                    print('ERROR: missing reduction step!')
                else:
                    print('ERROR: invalid or unavailable reduction step: {}'.format(redustep))
                print('Initial options are:')
                for redustep_ in defined_redusteps:
                    print('-rs/--reduction_step {}  (available: {})'.format(redustep_, defined_redusteps[redustep_]))
                raise SystemExit()

    # define instrument configuration dictionary
    instconf = bigdict[instrument]


    # check that the keywords of the requirements and the signature of the
    # different image types are all included in the masterkeywords list
    # or in the statistical summary
    statkeywords = list(statsumm(image2d=None).keys())
    for imagetype in instconf['imagetypes']:
        # check keywords in requirements
        allrequirements = list(instconf['imagetypes'][imagetype]['requirements'].keys()) + \
            list(instconf['imagetypes'][imagetype]['requirementx'].keys())
        for keyword in allrequirements:
            for operator in REQ_OPERATORS:
                lenop = len(operator)
                if keyword[-lenop:] == operator:
                    keyword = keyword[:-lenop]
                    break
            validkw = instconf['masterkeywords'] + statkeywords
            if keyword not in validkw:
                print('ERROR in configuration.yaml file')
                print('-> the (requirements) keyword {} is not included in the masterkeywords list '
                      'nor in the statistical keyword list '.format(keyword, statkeywords))
                raise SystemExit()

        # check keywords in signature
        for keyword in instconf['imagetypes'][imagetype]['signature']:
            if keyword not in instconf['masterkeywords']:
                print('ERROR in configuration.yaml file')
                print('-> the (signature) keyword {} is not included in the masterkeywords list'.format(keyword))
                raise SystemExit()

    if debug:
        print('* Instrument configuration: {}'.format(instconf))

    return instconf
