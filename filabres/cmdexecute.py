# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import re
import subprocess


class CmdExecute(object):
    def __init__(self, logfile=None):
        self.logfile = logfile

    def run(self, command, cwd=None):
        # define regex to filter out ANSI escape sequences
        ansi_regex = r'\x1b(' \
                     r'(\[\??\d+[hl])|' \
                     r'([=<>a-kzNM78])|' \
                     r'([\(\)][a-b0-2])|' \
                     r'(\[\d{0,2}[ma-dgkjqi])|' \
                     r'(\[\d+;\d+[hfy]?)|' \
                     r'(\[;?[hf])|' \
                     r'(#[3-68])|' \
                     r'([01356]n)|' \
                     r'(O[mlnp-z]?)|' \
                     r'(/Z)|' \
                     r'(\d+)|' \
                     r'(\[\?\d;\d0c)|' \
                     r'(\d;\dR))'
        ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)

        # display working directory
        if cwd is not None:
            msg = '[Working in {}]'.format(cwd)
            if self.logfile is None:
                print(msg)
            else:
                self.logfile.print(msg)

        # display command line
        msg = '$ {}'.format(command)
        if self.logfile is None:
            print(msg)
        else:
            self.logfile.print(msg)

        # execute command line
        p = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        pout = p.stdout.read().decode('utf-8')
        perr = p.stderr.read().decode('utf-8')
        p.stdout.close()
        p.stderr.close()
        if pout != '':
            if command[:4] == 'sex ':
                msg = ansi_escape.sub('', str(pout))
            else:
                msg = pout
            if self.logfile is None:
                print(msg)
            else:
                self.logfile.print(msg)
        if perr != '':
            if command[:4] == 'sex ':
                msg = ansi_escape.sub('', str(perr))
            else:
                msg = perr
            if self.logfile is None:
                print(msg)
            else:
                self.logfile.print(msg)
