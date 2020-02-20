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
from .list_classified import list_classified
from .list_reduced import list_reduced
from .load_instrument_configuration import load_instrument_configuration
from .load_setup import load_setup
from .nights_to_be_reduced import nights_to_be_reduced
from .run_reduction_step import run_reduction_step


def main():

    # parse command-line options
    parser = argparse.ArgumentParser(description="Basic data reduction of CAHA data")

    parser.add_argument("-rs", "--reduction_step", type=str, help="reduction step")
    parser.add_argument("-n", "--night", type=str, help="night label (wildcards are valid within quotes)")
    parser.add_argument("-i", "--interactive", action="store_true", help="enable interactive execution")
    parser.add_argument("-lc", "--lc_imagetype", type=str,
                        help="list classified images of the selected type with quantile information")
    parser.add_argument("-lcf", "--lcf_imagetype", type=str,
                        help="list classified images of the selected type in a single line")
    parser.add_argument("-k", "--keyword", type=str, action='append', nargs=1,
                        help="specify a keyword for the -lc option (ignored otherwise)")
    parser.add_argument("-lr", "--lr_imagetype", type=str,
                        help="list reduced images of the selected type with quantile information")
    parser.add_argument("-lrf", "--lrf_imagetype", type=str,
                        help="list reduced images of the selected type in a single line")
    parser.add_argument("-nd", "--ndecimal", type=int,
                        help="Number of decimal places for floats when using -lc or -lr", default=5)
    parser.add_argument("-s", "--setup", type=str, help="filabres setup file name")
    parser.add_argument("-v", "--verbose", action="store_true", help="display intermediate information while running")
    parser.add_argument("--debug", action="store_true", help="display debugging information")

    args = parser.parse_args()

    # ---

    instrument, datadir = load_setup(args.setup, args.verbose)
    datadir = check_tslash(datadir)

    if args.lc_imagetype is not None or args.lcf_imagetype is not None:
        list_classified(instrument=instrument,
                        img1=args.lc_imagetype,
                        img2=args.lcf_imagetype,
                        datadir=datadir,
                        args_night=args.night,
                        args_keyword=args.keyword,
                        args_ndecimal=args.ndecimal)

    if args.lr_imagetype is not None or args.lrf_imagetype is not None:
        list_reduced(instrument=instrument,
                     img1=args.lr_imagetype,
                     img2=args.lrf_imagetype,
                     args_night=args.night,
                     args_keyword=args.keyword,
                     args_ndecimal=args.ndecimal)

    # load instrument configuration
    instconf = load_instrument_configuration(
        instrument=instrument,
        redustep=args.reduction_step,
        verbose=args.verbose,
        debug=args.debug
    )

    # nights to be reduced
    list_of_nights = nights_to_be_reduced(args_night=args.night,
                                          datadir=datadir,
                                          verbose=args.verbose)

    # reduction steps
    if args.reduction_step == 'initialize':
        # initialize auxiliary databases (one for each observing night)
        initialize_auxdb(list_of_nights=list_of_nights,
                         instconf=instconf,
                         datadir=datadir,
                         verbose=args.verbose)
    else:
        # execute reduction step
        run_reduction_step(redustep=args.reduction_step,
                           interactive=args.interactive,
                           datadir=datadir,
                           list_of_nights=list_of_nights,
                           instconf=instconf,
                           verbose=args.verbose,
                           debug=args.debug)

    print('* program STOP')
    raise SystemExit()


if __name__ == "__main__":

    main()
