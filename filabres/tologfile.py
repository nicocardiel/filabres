# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#


class ToLogFile(object):
    """
    Auxiliary class to generate a log file.
    """
    def __init__(self, workdir=None, basename=None, verbose=False):
        if workdir is None:
            self.fname = '{}'.format(basename)
        else:
            self.fname = '{}/{}'.format(workdir, basename)
        self.logfile = open(self.fname, 'wt')
        self.verbose = verbose

    def print(self, line, f=False):
        if self.verbose or f:  # f = forced print
            print(line)
        if not self.logfile.closed:
            self.logfile.write(line + '\n')
            self.logfile.flush()

    def close(self):
        self.logfile.close()
