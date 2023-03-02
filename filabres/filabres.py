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
import sys

from .check_args_compatibility import check_args_compatibility
from .check_datadir import check_datadir
from .delete_reduced import delete_reduced
from .generate_setup import generate_setup
from .classify_images import classify_images
from .list_classified import list_classified
from .list_originf import list_originf
from .list_reduced import list_reduced
from .load_instrument_configuration import load_instrument_configuration
from .load_setup import load_setup
from .nights_to_be_reduced import nights_to_be_reduced
from .run_calibration_step import run_calibration_step
from .run_reduction_step import run_reduction_step
from .version import version


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
    group_delet = parser.add_argument_group('delete reduced calibration')
    group_lists = parser.add_argument_group('lists of classified or reduced images')
    group_other = parser.add_argument_group('other auxiliary arguments')

    # group_setup
    group_setup.add_argument("--setup", type=str, nargs=2, help="generate setup_filabres.yaml",
                             metavar=('INSTRUMENT', 'DATADIR'))

    # group_check
    group_check.add_argument("--check", action="store_true",
                             help="check original FITS files in DATADIR are not repeated")

    # group_reduc
    group_reduc.add_argument("-rs", "--reduction_step", type=str, nargs='?', const="None")
    group_reduc.add_argument("-f", "--force", action="store_true", help="force reduction of already reduced files")
    group_reduc.add_argument("-na", "--no_astrometry", action="store_true",
                             help="do not perform astrometry calibration")
    group_reduc.add_argument("-ng", "--no_reuse_gaia", action="store_true",
                             help="do not reuse pevious GAIA data to perform the initial astrometric calibration"
                                  " (with Astrometry.net tools)")
    group_reduc.add_argument("-i", "--interactive", action="store_true", help="enable interactive execution")
    group_reduc.add_argument("--filename", type=str,
                             help="particular image to be reduced (only valid for science images; without path)")

    # group_delet
    group_delet.add_argument("--delete", type=str, help="delete reduced image",
                             metavar='REDUCED_IMAGE')

    # group_lists
    group_lists.add_argument("-lc", "--list_classified", type=str, nargs='?', const="None",
                             help="list classified images of the selected type (with additional keyword information)",
                             metavar='REDUCTION_STEP')
    group_lists.add_argument("-lr", "--list_reduced", type=str, nargs='?', const="None",
                             help="list reduced images of the selected type (with additional keyword information)",
                             metavar='REDUCTION_STEP')
    group_lists.add_argument("-of", "--originf", type=str, help="list original individual images employed to "
                                                                "generate a particular reduced calibration image")
    group_lists.add_argument("-lm", "--list_mode", type=str, help="display mode for list of files",
                             choices=["long", "singleline", "basic"], metavar='MODE')
    group_lists.add_argument("-k", "--keyword", type=str, action='append', nargs=1,
                             help="keyword for the -lc/-lr option")
    group_lists.add_argument("-ks", "--keyword_sort", type=str, action='append', nargs=1,
                             help="sorting keyword for the -lc/-lr option")
    group_lists.add_argument("--filter", type=str, help="filter list by evaluating logical expression",
                             metavar='EXPRESSION')
    group_lists.add_argument("-pxy", "--plotxy", action="store_true", help="display scatter plots when listing files")
    group_lists.add_argument("-pi", "--plotimage", action="store_true", help="display images when listing files")
    group_lists.add_argument("-nd", "--ndecimal", type=int,
                             help="Number of decimal places for floats when using -lc/-lr",
                             metavar='INTEGER')

    # other arguments
    group_other.add_argument("-n", "--night", type=str, help="night label (wildcards are valid within quotes)")
    group_other.add_argument("-v", "--verbose", action="store_true",
                             help="display intermediate information while running")
    group_other.add_argument("--debug", action="store_true", help="display debugging information")

    args = parser.parse_args()

    print(f'Welcome to filabres, version {version}\n')

    if len(sys.argv) == 1:
        parser.print_usage()
        raise SystemExit()

    # ---

    # check argument compatibility
    check_args_compatibility(args, debug=False)

    # set default values that cannot be set
    if args.list_mode is None:
        args.list_mode = 'long'

    # generate setup_filabres.yaml if required
    if args.setup is not None:
        generate_setup(args.setup)
        print('* program STOP')
        raise SystemExit()

    # load setup file
    setupdata = load_setup(args.verbose)

    # delete reduced image
    if args.delete is not None:
        delete_reduced(setupdata=setupdata,
                       reducedima=args.delete)
        print('* program STOP')
        raise SystemExit()

    # initial image check
    if args.check:
        check_datadir(setupdata, args.verbose)
        print('* program STOP')
        raise SystemExit()

    # lists of classified images
    if args.list_classified is not None:
        if args.list_reduced is not None or args.originf is not None:
            print("-lc is incompatible with either -lr or -of")
            raise SystemExit()
        list_classified(setupdata=setupdata,
                        img=args.list_classified,
                        list_mode=args.list_mode,
                        args_night=args.night,
                        args_keyword=args.keyword,
                        args_keyword_sort=args.keyword_sort,
                        args_filter=args.filter,
                        args_plotxy=args.plotxy,
                        args_plotimage=args.plotimage,
                        args_ndecimal=args.ndecimal)
        raise SystemExit()

    # list of reduced images
    if args.list_reduced is not None:
        if args.list_classified is not None or args.originf is not None:
            print("-lr is incompatible with either -lc or -of")
            raise SystemExit()
        list_reduced(setupdata=setupdata,
                     img=args.list_reduced,
                     list_mode=args.list_mode,
                     args_night=args.night,
                     args_keyword=args.keyword,
                     args_keyword_sort=args.keyword_sort,
                     args_filter=args.filter,
                     args_plotxy=args.plotxy,
                     args_plotimage=args.plotimage,
                     args_ndecimal=args.ndecimal)
        raise SystemExit()

    if args.originf is not None:
        if args.list_classified is not None or args.list_reduced is not None:
            print("-of is incompatible with either -lc or -lr")
            raise SystemExit()
        list_originf(setupdata=setupdata,
                     args_originf=args.originf,
                     list_mode=args.list_mode,
                     args_keyword=args.keyword,
                     args_keyword_sort=args.keyword_sort,
                     args_filter=args.filter,
                     args_plotxy=args.plotxy,
                     args_plotimage=args.plotimage,
                     args_ndecimal=args.ndecimal)
        raise SystemExit()

    # load instrument configuration
    instconf = load_instrument_configuration(
        setupdata=setupdata,
        redustep=args.reduction_step,
        verbose=args.verbose,
        debug=args.debug
    )

    # nights to be reduced
    list_of_nights = nights_to_be_reduced(args_night=args.night,
                                          setupdata=setupdata,
                                          verbose=args.verbose)

    # reduction steps
    if args.reduction_step == 'initialize':
        # check --singleimage is not set
        if args.filename is not None:
            msg = 'Argument --filename is invalid for --rs initialize'
            raise SystemError(msg)
        if args.no_reuse_gaia or args.no_astrometry:
            msg = 'Argument --no_reuse_gaia / --no_astrometry are invalid for --rs initialize'
            raise SystemError(msg)
        # initialize auxiliary databases (one for each observing night)
        classify_images(list_of_nights=list_of_nights,
                        instconf=instconf,
                        setupdata=setupdata,
                        force=args.force,
                        verbose=args.verbose)
    else:
        classification = instconf['imagetypes'][args.reduction_step]['classification']
        if classification == 'calibration':
            # check --singleimage is not set
            if args.filename is not None:
                msg = 'Argument --filename is invalid for calibration reduction steps'
                raise SystemError(msg)
            if args.no_reuse_gaia or args.no_astrometry:
                msg = 'Argument --no_reuse_gaia / --no_astrometry are invalid for calibration reduction steps'
                raise SystemError(msg)
            # execute reduction step
            run_calibration_step(redustep=args.reduction_step,
                                 setupdata=setupdata,
                                 list_of_nights=list_of_nights,
                                 instconf=instconf,
                                 force=args.force,
                                 verbose=args.verbose,
                                 debug=args.debug)
        elif classification == 'science':
            # execute reduction step
            run_reduction_step(redustep=args.reduction_step,
                               interactive=args.interactive,
                               setupdata=setupdata,
                               list_of_nights=list_of_nights,
                               filename=args.filename,
                               no_astrometry=args.no_astrometry,
                               no_reuse_gaia=args.no_reuse_gaia,
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
