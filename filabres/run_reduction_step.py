from astropy.io import fits
import datetime
import json
import numpy as np
import os
import sys

from .version import version

from filabres import LISTDIR


def getkey_from_signature(signature, key):
    """
    Return key from signature

    Parameters
    ==========
    signature: dictionary
        Python dictionary storing the signature keywords.
    key : str
        Keyword to be obtained from signature
    """
    if key not in signature:
        print('* ERROR: {} not found in signature'.format(key))
        raise SystemExit()
    else:
        return signature[key]


def signature_string(signature):
    """
    Return signature string.

    Parameters
    ==========
    signature : dict
        Signature dictionary.

    Returns
    =======
    sortedkeys : list
        List of signature keys in alphabetic order.
    output : str
        String sequence with the values of the different signature
        keywords in alphabetic order.
    """

    sortedkeys = list(signature.keys())
    sortedkeys.sort()
    output = ''
    for i, key in enumerate(sortedkeys):
        if i != 0:
            output += '__'
        output += str(signature[key])
    return sortedkeys, output


def run_reduction_step(redustep, datadir, list_of_nights, instconf,
                       database, verbose):
    """
    Execute reduction step.

    Parameters
    ==========
    redustep : str
        Reduction step to be executed.
    datadir : str
        Data directory containing the different nights to be reduced.
    list_of_nights : list
        List of nights matching the selection filter.
    instconf : dict
        Instrument configuration. See file configuration.json for
        details.
    database: dict
        Output database where the relevant information of the reduced
        images is stored: signature, path and file name.
    verbose : bool
        If True, display intermediate information.
    """

    # check for subdirectory
    if os.path.isdir(redustep):
        if verbose:
            print('Subdirectory {} found'.format(redustep))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(redustep))
        os.makedirs(redustep)

    # prepare main database
    if redustep not in database:
        database[redustep] = dict()

    # loop in night
    for night in list_of_nights:
        # read local database for current night
        jsonfilename = LISTDIR + night + '/imagedb_' + \
                       instconf['instname'] + '.json'
        if verbose:
            print('* Reading file {}'.format(jsonfilename))
        try:
            with open(jsonfilename) as jfile:
                imagedb = json.load(jfile)
        except FileNotFoundError:
            print('ERROR: file {} not found'.format(jsonfilename))
            print('Try using -rs initialize')
            raise SystemExit()
        # check version of instrument configuration
        if instconf['version'] != imagedb['metainfo']['instconf']['version']:
            print('ERROR: different versions of instrument configuration')
            raise SystemExit()
        # select images of the requested type
        list_of_images = imagedb['lists'][redustep]
        nlist_of_images = len(list_of_images)
        if verbose:
            print('* Number of {} images found {}'.format(
                redustep, nlist_of_images))
        if nlist_of_images > 0:
            nightdir = redustep + '/' + night
            if os.path.isdir(nightdir):
                if verbose:
                    print('Subdirectory {} found'.format(nightdir))
            else:
                if verbose:
                    print('Subdirectory {} not found. '
                          'Creating it!'.format(nightdir))
                os.makedirs(nightdir)
            signaturekeys = instconf['imagetypes'][redustep]['signature']
            # determine number of different signatures
            list_of_signatures = []
            for filename in list_of_images:
                # signature of particular image
                imgsignature = dict()
                for key in signaturekeys:
                    imgsignature[key] = imagedb['allimages'][filename][key]
                if len(list_of_signatures) == 0:
                    list_of_signatures.append(imgsignature)
                else:
                    signaturefound = False
                    for dumsignature in list_of_signatures:
                        if dumsignature == imgsignature:
                            signaturefound = True
                            break
                    if not signaturefound:
                        list_of_signatures.append(imgsignature)
            if verbose:
                nsignatures = len(list_of_signatures)
                print('* Number of different signatures found:', nsignatures)
            # select images with a common signature and compute combination
            for isignature in range(len(list_of_signatures)):
                signature = list_of_signatures[isignature]
                images_with_fixed_signature = []
                for filename in list_of_images:
                    # signature of particular image
                    imgsignature = dict()
                    for key in signaturekeys:
                        imgsignature[key] = imagedb['allimages'][filename][key]
                    if imgsignature == signature:
                        images_with_fixed_signature.append(
                            datadir + night + '/' + filename)
                nfiles = len(images_with_fixed_signature)
                if nfiles == 0:
                    print('* ERROR: unexpected number of {} images = 0'.format(
                        nfiles))
                    raise SystemExit()
                if verbose:
                    print('- signature:')
                    for key in signature:
                        print(key, signature[key])
                    print('- Number of images with this signature:',
                          len(images_with_fixed_signature))
                    for filename in images_with_fixed_signature:
                        print(filename, end=' ')
                    print()
                if redustep == 'bias':  # median combination
                    # declare temporary cube to store all the images
                    naxis1 = getkey_from_signature(signature, 'NAXIS1')
                    naxis2 = getkey_from_signature(signature, 'NAXIS2')
                    image3d = np.zeros((nfiles, naxis2, naxis1),
                                       dtype=np.float32)
                    output_header = None
                    output_filename = nightdir + '/bias{:04d}.fits'.format(
                        isignature + 1)
                    print('-> output filename {}'.format(output_filename))
                    for i in range(nfiles):
                        filename = images_with_fixed_signature[i]
                        with fits.open(filename) as hdulist:
                            image_header = hdulist[0].header
                            image_data = hdulist[0].data
                        if i == 0:
                            output_header = image_header
                            # avoid warning when saving FITS
                            if output_header['BLANK']:
                                del output_header['BLANK']
                            output_header.add_history("---")
                            output_header.add_history(
                                'Using filabres v.{}'.format(version))
                            output_header.add_history('Date: ' +
                                str(datetime.datetime.utcnow().isoformat()))
                            output_header.add_history(sys.argv)
                            output_header.add_history(
                                'Computing median {} from:'.format(redustep))
                        image3d[i, :, :] += image_data
                        output_header.add_history(
                            os.path.basename(filename))
                    output_header.add_history('Signature: ' + str(signature))
                    image2d = np.median(image3d, axis=0)
                    hdu = fits.PrimaryHDU(image2d.astype(np.float32),
                                          output_header)
                    hdu.writeto(output_filename, overwrite=True)
                    # generate string with signature values
                    sortedkeys, key = signature_string(signature)
                    if 'sortedkeys' not in database[redustep]:
                        database[redustep]['sortedkeys'] = sortedkeys
                    # update main database with redustep if not present
                    if key not in database[redustep]:
                        database[redustep][key] = dict()
                    # update database with result using MJD-OBS as index
                    mjdobs = '{:.5f}'.format(output_header['MJD-OBS'])
                    database[redustep][key][mjdobs] = output_filename
                else:
                    print('* ERROR: combination of {} not implemented yet'.format(
                        redustep))
                    raise SystemExit()
        else:
            # skipping night (no images of sought type)
            if verbose:
                print('- No {} images found. Skipping night!'.format(redustep))
