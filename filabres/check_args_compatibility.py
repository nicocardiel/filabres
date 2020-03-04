def check_args_compatibility(args, debug=False):
    """
    Check whether the input arguments are compatible.

    Parameters
    ----------
    args : argparse.Namespace object
        Input arguments.
    debug : bool
        If True, display list of arguments, with their value and type.
    """

    expected_args = vars(args)

    if debug:
        for arg in expected_args:
            print(arg, getattr(args, arg), type(getattr(args, arg)))

    # create a list for each group
    arglist_check = ['check']
    arglist_reduc = ['reduction_step', 'force', 'interactive']
    arglist_lists = ['lc_imagetype', 'lr_imagetype', 'listmode', 'keyword',
                     'keyword_sort', 'plotxy', 'plotimage', 'ndecimal']
    arglist_other = ['night', 'setup', 'verbose', 'debug']

    # concatenate the above lists
    total_arglist = arglist_check + arglist_reduc + arglist_lists + arglist_other

    # check that all the expected arguments are included in the group lists
    msg = None
    for arg in expected_args:
        if arg not in total_arglist:
            msg = 'ERROR: argument {} is not included in total_arglist'.format(arg)
    if msg is not None:
        raise SystemError(msg)

    # check that all the arguments in the group lists are expected
    for arg in total_arglist:
        if arg not in expected_args:
            msg = 'ERROR: argument {} is not included in expected_args'.format(arg)
    if msg is not None:
        raise SystemError(msg)

    # check for incompatibilities between arguments belonging to different groups
    msg = None
    for ll in [[arglist_check, arglist_reduc],
               [arglist_check, arglist_lists],
               [arglist_reduc, arglist_lists]]:
        list1 = ll[0]
        list2 = ll[1]
        for arg1 in list1:
            val1 = getattr(args, arg1)
            if isinstance(val1, bool):
                if val1:
                    for arg2 in list2:
                        val2 = getattr(args, arg2)
                        if isinstance(val2, bool):
                            if val2:
                                msg = 'ERROR1: arguments --{} and --{} are incompatible'.format(arg1, arg2)
                        else:
                            if val2 is not None:
                                msg = 'ERROR2: arguments --{} and --{} are incompatible'.format(arg1, arg2)
            else:
                if val1 is not None:
                    for arg2 in list2:
                        val2 = getattr(args, arg2)
                        if isinstance(val2, bool):
                            if val2:
                                msg = 'ERROR3: arguments --{} and --{} are incompatible'.format(arg1, arg2)
                        else:
                            if val2 is not None:
                                msg = 'ERROR4: arguments --{} and --{} are incompatible'.format(arg1, arg2)

    if msg is not None:
        print(msg)
        raise SystemExit()
