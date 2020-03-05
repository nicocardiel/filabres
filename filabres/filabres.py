# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

"""
Basic data reduction of astronomical images.

At present, the code performs the following tasks:
- Image classification (bias, flat-imaging, science-imaging, etc.)
- Reduction of calibration images (bias, flat-imaging, etc.) and generation
  of combined master calibrations as a function of the modified Julian Date.
- Basic reduction of individual science images, making use of the corresponding
  master calibration (closest in time to the observation of the science target).
  The main reduction steps are:
  - bias subtraction
  - flatfielding of the images
  - astrometric calibration

This code is hosted at: https://github.com/nicocardiel/filabres
Maintainer: Nicolás Cardiel <cardiel@ucm.es>
"""

import argparse

from .check_args_compatibility import check_args_compatibility
from .check_datadir import check_datadir
from .check_tslash import check_tslash
from .generate_setup import generate_setup
from .initialize_auxdb import initialize_auxdb
from .list_classified import list_classified
from .list_reduced import list_reduced
from .load_instrument_configuration import load_instrument_configuration
from .load_setup import load_setup
from .nights_to_be_reduced import nights_to_be_reduced
from .run_calibration_step import run_calibration_step
from .run_reduction_step import run_reduction_step


def main():

    # parse command-line options
    parser = argparse.ArgumentParser(description="Basic data reduction of astronomical images")

    # note 1: do not use default=... in add_argument() to have those
    # arguments set to None, which is necessary for the compatibility check
    # performed below; the default values can be set after the call to the
    # check_args_compatibility() function

    # note 2: include new groups and arguments in check_args_compatibility() function

    # define argument groups
    group_setup = parser.add_argument_group('generation of initial setup_filabres.yaml')
    group_check = parser.add_argument_group('initial check')
    group_reduc = parser.add_argument_group('initialization and reduction of the data')
    group_lists = parser.add_argument_group('lists of classified or reduced images')
    group_other = parser.add_argument_group('other auxiliary arguments')

    # group_setup
    group_setup.add_argument("--setup", type=str, nargs=2, help="generate setup_filabres.yaml",
                             metavar=('INSTRUMENT', 'DATADIR'))

    # group_check
    group_check.add_argument("--check", action="store_true",
                             help="check original FITS files in DATADIR are not repeated")

    # group_reduc
    group_reduc.add_argument("-rs", "--reduction_step", type=str)
    group_reduc.add_argument("-f", "--force", action="store_true", help="force reduction of already reduced files")
    group_reduc.add_argument("-i", "--interactive", action="store_true", help="enable interactive execution")

    # group_lists
    group_lists.add_argument("-lc", "--lc_imagetype", type=str, nargs='*',
                             help="list classified images of the selected type with quantile information",
                             metavar=('REDUCTION_STEP'))
    group_lists.add_argument("-lr", "--lr_imagetype", type=str, nargs='*',
                             help="list reduced images of the selected type with quantile information",
                             metavar=('REDUCTION_STEP'))
    group_lists.add_argument("-lm", "--listmode", type=str, help="display mode for list of files",
                             choices=["long", "singleline", "basic"], metavar=('MODE'))
    group_lists.add_argument("-k", "--keyword", type=str, action='append', nargs=1,
                             help="keyword for the -lc/-lr option")
    group_lists.add_argument("-ks", "--keyword_sort", type=str, action='append', nargs=1,
                             help="sorting keyword for the -lc/-lr option")
    group_lists.add_argument("-pxy", "--plotxy", action="store_true", help="display scatter plots when listing files")
    group_lists.add_argument("-pi", "--plotimage", action="store_true", help="display images when listing files")
    group_lists.add_argument("-nd", "--ndecimal", type=int,
                             help="Number of decimal places for floats when using -lc/-lr")

    # other arguments
    group_other.add_argument("-n", "--night", type=str, help="night label (wildcards are valid within quotes)")
    group_other.add_argument("-v", "--verbose", action="store_true",
                             help="display intermediate information while running")
    group_other.add_argument("--debug", action="store_true", help="display debugging information")

    args = parser.parse_args()

    # ---

    # check argument compatibility
    check_args_compatibility(args, debug=False)

    # set default values
    if args.listmode is None:
        args.listmode = 'long'
    if args.ndecimal is None:
        args.ndecimal = 5

    # generate setup_filabres.yaml if required
    if args.setup is not None:
        generate_setup(args.setup)

    instrument, datadir, ignored_images_file, image_header_corrections_file = load_setup(args.verbose)
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
