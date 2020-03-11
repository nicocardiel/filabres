#
# Copyright 2015-2020 Universidad Complutense de Madrid
#
# This file is part of Numina
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import argparse
import glob
import os.path


class FileInfo(object):
    """Auxiliary class to store fname and associated information.

    Parameters
    ----------
    fname : string
        File name.
    fileinfo : list of strings or None
        Associated file information.

    Attributes
    ----------
    The same as the parameters.

    """

    def __init__(self, fname, extnum=None, fileinfo=None):
        self.fname = fname
        self.extnum = extnum
        self.fileinfo = fileinfo

    def __str__(self):
        """Printable representation of a FileInfo instance."""

        output = "<FileInfo instance>\n" + \
                 "- fname: " + self.fname + "\n" + \
                 "- extnum..: " + self.extnum + "\n" + \
                 "- fileinfo: " + str(self.fileinfo)

        return output


def check_extnum(fname):
    """Return extension number when given as fname.fits[extnum]

    Parameters
    ----------
    fname : string
        File name.

    Returns
    -------
    fname : string
        File name without the extension number (if initially present).
    extnum : int or None
        Extension number.

    """

    extnum = None
    if fname[-1] == ']':
        leftbracket = fname.rfind('[')
        if leftbracket != -1:
            cdum = fname[(leftbracket + 1):-1]
            if len(cdum) > 0:
                try:
                    extnum = int(cdum)
                except ValueError:
                    raise ValueError("Invalid extension number {}".format(
                        fname[(leftbracket + 1):-1]
                    ))
                # remove extension number from file name
                fname = fname[:leftbracket]

    return fname, extnum


def list_fileinfo_from_txt(fname):
    """Returns a list of FileInfo instances if fname is a TXT file.
    
    Parameters
    ----------
    fname : string
        Name of a file (wildcards are acceptable) or a TXT file
        containing a list of files. Empty Lines, and lines starting by
        a hash or a at symbol in the TXT file are ignored.
    
    Returns
    -------
    output : list of FileInfo instances
        List of FileInfo instances containing the name of the files
        and additional file information.
        
    """
    
    # check for input file
    if not os.path.isfile(fname):
        # check for wildcards
        list_fits_files = glob.glob(fname)
        if len(list_fits_files) == 0:
            # check for extension at the end of the file name
            tmpfile, tmpextnum = check_extnum(fname)
            list_fits_files = glob.glob(tmpfile)
            if len(list_fits_files) == 0:
                raise ValueError("File " + fname + " not found!")
            else:
                list_fits_files.sort()
                output = [FileInfo(tmpfile, tmpextnum) for
                          tmpfile in list_fits_files]
                return output
        else:
            list_fits_files.sort()
            output = [FileInfo(tmpfile) for tmpfile in list_fits_files]
            return output

    # if input file is a txt file, assume it is a list of FITS files
    if fname[-4:] == ".txt":
        with open(fname) as f:
            file_content = f.read().splitlines()
        output = []
        for line in file_content:
            if len(line) > 0:
                if line[0] not in ['#', '@']:
                    tmplist = line.split()
                    tmpfile = tmplist[0]
                    tmpextnum = None
                    if len(tmplist) > 1:
                        tmpinfo = tmplist[1:]
                    else:
                        tmpinfo = None
                    if not os.path.isfile(tmpfile):
                        # check for extension
                        tmpfile, tmpextnum = check_extnum(tmpfile)
                        if tmpextnum is None:
                            raise ValueError("File {} not found".format(
                                tmpfile))
                        else:
                            if not os.path.isfile(tmpfile):
                                raise ValueError("File {} not found".format(
                                    tmpfile))

                    output.append(FileInfo(tmpfile, tmpextnum, tmpinfo))
    else:
        output = [FileInfo(fname)]

    return output


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(prog='fileinfo')
    parser.add_argument("txt_file",
                        help="txt file with list files")
    args = parser.parse_args(args)

    # execute function
    list_fileinfo = list_fileinfo_from_txt(args.txt_file)
    for item in list_fileinfo:
        print(item)

if __name__ == "__main__":

    main()
