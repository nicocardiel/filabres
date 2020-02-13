# -*- coding: utf-8 -*-

"""
Basic data reduction of CAHA data.

Project started with the "Prácticas en Empresa" of Enrique Galcerán García
(Astrophysics Master, Universidad Complutense de Madrid, course 2018-2019).
See details in: https://github.com/enriquegalceran/PE-CAHA

The basic ideas from Galcerán's project have been used by Nicolás Cardiel to
implement filabres, trying to speed up the execution time and generalizing
the algorithms to be useful for additional instruments and observing modes.

This code is hosted at: https://github.com/nicocardiel/filabres
"""

import argparse

from .check_tslash import check_tslash
from .initialize_auxdb import initialize_auxdb
from .load_instrument_configuration import load_instrument_configuration
from .nights_to_be_reduced import nights_to_be_reduced
from .run_reduction_step import run_reduction_step


def main():

    # parse command-line options
    parser = argparse.ArgumentParser(
        description="Basic data reduction of CAHA data"
    )

    parser.add_argument("-q", "--quiet", action="store_true",
                        help="run quietly (reduced verbosity)")
    parser.add_argument("-i", "--instrument", type=str,
                        help="instrument identification")
    parser.add_argument("-rs", "--reduction_step", type=str,
                        help="reduction step")
    parser.add_argument("-dd", "--datadir", type=str,
                        help='data directory')
    parser.add_argument("-db", "--database", type=str,
                        help='database file name (')
    parser.add_argument("-n", "--night", type=str,
                        help="night label (wildcards are valid withing "
                             "quotes)")
    parser.add_argument("--debug", action="store_true",
                        help="display debugging information")

    args = parser.parse_args()

    # ---

    # set verbosity
    verbose = not args.quiet

    # load instrument configuration
    instrument = args.instrument
    redustep = args.reduction_step
    instconf = load_instrument_configuration(
        instrument=instrument,
        redustep=redustep,
        verbose=False
    )

    # data directory
    datadir = args.datadir
    if datadir is None:
        print('ERROR: -dd/--datadir DATADIR missing!')
        raise SystemExit()
    else:
        # add trailing slash if not present
        datadir = check_tslash(dir=datadir)

    # nights to be reduced
    list_of_nights = nights_to_be_reduced(datadir=datadir,
                                          args_night=args.night,
                                          verbose=verbose)

    # reduction steps
    if redustep == 'initialize':
        # initialize auxiliary databases (one for each observing night)
        initialize_auxdb(datadir=datadir,
                         list_of_nights=list_of_nights,
                         instconf=instconf,
                         verbose=verbose)
    else:
        # execute reduction step
        run_reduction_step(args_database=args.database,
                           redustep=redustep,
                           datadir=datadir,
                           list_of_nights=list_of_nights,
                           instconf=instconf,
                           verbose=verbose,
                           debug=args.debug)

    print('* program STOP')
    raise SystemExit()


if __name__ == "__main__":

    main()
