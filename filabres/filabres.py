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

from .check_datadir import check_datadir
from .check_tslash import check_tslash
from .initialize_auxdb import initialize_auxdb
from .list_classified import list_classified
from .list_reduced import list_reduced
from .load_instrument_configuration import load_instrument_configuration
from .load_setup import load_setup
from .nights_to_be_reduced import nights_to_be_reduced
from .run_calibration_step import run_calibration_step
from .run_reduction_step import run_reduction_step


# ToDo:
#       bias: poner restricción en STD robusta?
#       salvar tabla de objetos de sextractor,...
#       medir PSFs con astromatic
#       mirar argparse para agrupar parametros por grupos compatibles/incompatibles

def main():

    # parse command-line options
    parser = argparse.ArgumentParser(description="Basic data reduction of CAHA data")

    parser.add_argument("--check", action="store_true", help="check original FITS files in DATADIR are not repeated")
    parser.add_argument("-rs", "--reduction_step", type=str, help="reduction step")
    parser.add_argument("-f", "--force", action="store_true", help="force reduction of already reduced files")
    parser.add_argument("-n", "--night", type=str, help="night label (wildcards are valid within quotes)")
    parser.add_argument("-i", "--interactive", action="store_true", help="enable interactive execution")
    parser.add_argument("-lc", "--lc_imagetype", type=str, nargs='*',
                        help="list classified images of the selected type with quantile information")
    parser.add_argument("-lr", "--lr_imagetype", type=str, nargs='*',
                        help="list reduced images of the selected type with quantile information")
    parser.add_argument("-lm", "--listmode", type=str, help="display mode for list of files",
                        choices=["long", "singleline", "basic"], default="long")
    parser.add_argument("-k", "--keyword", type=str, action='append', nargs=1,
                        help="keyword for the -lc/-lr option")
    parser.add_argument("-ks", "--keyword_sort", type=str, action='append', nargs=1,
                        help="sorting keyword for the -lc/-lr option")
    parser.add_argument("-pxy", "--plotxy", action="store_true", help="display scatter plots when listing files")
    parser.add_argument("-pi", "--plotimage", action="store_true", help="display images when listing files")
    parser.add_argument("-nd", "--ndecimal", type=int,
                        help="Number of decimal places for floats when using -lc or -lr", default=5)
    parser.add_argument("-s", "--setup", type=str, help="filabres setup file name")
    parser.add_argument("-v", "--verbose", action="store_true", help="display intermediate information while running")
    parser.add_argument("--debug", action="store_true", help="display debugging information")

    args = parser.parse_args()

    # ---

    instrument, datadir, image_corrections_file = load_setup(args.setup, args.verbose)
    datadir = check_tslash(datadir)

    if args.check:
        check_datadir(datadir)
        print('* program STOP')
        raise SystemExit()

    if args.lc_imagetype is not None:
        list_classified(instrument=instrument,
                        img=args.lc_imagetype,
                        listmode=args.listmode,
                        datadir=datadir,
                        args_night=args.night,
                        args_keyword=args.keyword,
                        args_keyword_sort=args.keyword_sort,
                        args_plotxy=args.plotxy,
                        args_plotimage=args.plotimage,
                        args_ndecimal=args.ndecimal)

    if args.lr_imagetype is not None:
        list_reduced(instrument=instrument,
                     img=args.lr_imagetype,
                     listmode=args.listmode,
                     args_night=args.night,
                     args_keyword=args.keyword,
                     args_keyword_sort=args.keyword_sort,
                     args_plotxy=args.plotxy,
                     args_plotimage=args.plotimage,
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
                         force=args.force,
                         image_corrections_file=image_corrections_file,
                         verbose=args.verbose)
    else:
        classification = instconf['imagetypes'][args.reduction_step]['classification']
        if classification == 'calibration':
            run_calibration_step(redustep=args.reduction_step,
                                 datadir=datadir,
                                 list_of_nights=list_of_nights,
                                 instconf=instconf,
                                 force=args.force,
                                 verbose=args.verbose,
                                 debug=args.debug)
        elif classification == 'science':
            run_reduction_step(redustep=args.reduction_step,
                               interactive=args.interactive,
                               datadir=datadir,
                               list_of_nights=list_of_nights,
                               instconf=instconf,
                               force=args.force,
                               verbose=args.verbose,
                               debug=args.debug)
        else:
            msg = 'Invalid reduction step: {}'.format(args.reduction_step)
            raise SystemError(msg)

    print('* program STOP')
    raise SystemExit()


if __name__ == "__main__":

    main()
