# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from collections import OrderedDict
import datetime
import os
import sys
import yaml

from filabres import version


# see https://stackoverflow.com/questions/31605131/
# (dumping-a-dictionary-to-a-yaml-file-while-preserving-order)
def represent_dictionary_order(self, dict_data):
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    yaml.add_representer(OrderedDict, represent_dictionary_order)


def generate_setup(args_setup):
    """
    Generate initial YAML files.

    The files generated are:
    - setup_filabres.yaml
    - ignored_images.yaml
    - image_header_corrections.yaml

    Parameters
    ==========
    args_setup : list of str
        Instrument and datadir.

    """

    yaml_filename1 = 'setup_filabres.yaml'
    yaml_filename2 = 'ignored_images.yaml'
    yaml_filename3 = 'image_header_corrections.yaml'
    lfiles = [yaml_filename1, yaml_filename2, yaml_filename3]

    # avoid file overwriting
    for yaml_filename in lfiles:
        if os.path.isfile(yaml_filename):
            print('ERROR: the file "{}" already exists.'.format(yaml_filename))
            print('-> Delete it manually before executing filabres.')
            raise SystemExit()

    # generate an ordered dictionary for the 'setup_filabres.yaml'
    setup_yaml()
    d = OrderedDict()
    d['instrument'] = args_setup[0]
    d['datadir'] = args_setup[1]
    d['ignored_images_file'] = yaml_filename2
    d['image_header_corrections_file'] = yaml_filename3
    with open(yaml_filename1, 'wt') as f:
        yaml.dump(d, f, default_flow_style=False)

    # include comments in all the files
    for yaml_filename in lfiles:
        header = '# file {}\n#\n'.format(yaml_filename)
        header += '# generated automatically by {} v.{}\n#\n'.format(
            os.path.basename(sys.argv[0]), version
        )
        header +='# creation date {}\n#\n'.format(datetime.datetime.utcnow().isoformat())
        if os.path.isfile(yaml_filename):
            with open(yaml_filename, 'r+t') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(header + content)
        else:
            with open(yaml_filename, 'wt') as f:
                f.write(header)
        print('File {} created!'.format(yaml_filename))

    raise SystemExit()
