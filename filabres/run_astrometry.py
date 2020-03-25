# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from astropy import units as u
from astropy.coordinates import SkyCoord, FK5
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import glob
import json
import numpy as np
import os
import pkgutil
import re
import subprocess

from .load_scamp_cat import load_scamp_cat
from .retrieve_gaia import retrieve_gaia
from .plot_astrometry import plot_astrometry

NMAXGAIA = 2000


class ToLogFile(object):
    def __init__(self, workdir, verbose):
        self.fname = '{}/astrometry.log'.format(workdir)
        self.logfile = open(self.fname, 'wt')
        self.verbose = verbose

    def print(self, line):
        if self.verbose:
            print(line)
        if not self.logfile.closed:
            self.logfile.write(line + '\n')
            self.logfile.flush()

    def close(self):
        self.logfile.close()


class CmdExecute(object):
    def __init__(self, logfile):
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

        if cwd is not None:
            self.logfile.print('[Working in {}]'.format(cwd))
        self.logfile.print('$ {}'.format(command))
        p = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        pout = p.stdout.read().decode('utf-8')
        perr = p.stderr.read().decode('utf-8')
        p.stdout.close()
        p.stderr.close()
        if pout != '':
            if command[:4] == 'sex ':
                self.logfile.print(ansi_escape.sub('', str(pout)))
            else:
                self.logfile.print(pout)
        if perr != '':
            if command[:4] == 'sex ':
                self.logfile.print(ansi_escape.sub('', str(perr)))
            else:
                self.logfile.print(perr)


def save_auxfiles(output_fname, nightdir, workdir, cmd, verbose):
    """
    Auxiliary function to store relevant files after astrometric calibration

    Parameters
    ----------
    output_fname : str or None
        Output file name.
    nightdir : str
        Directory where the reduced images will be stored.
    workdir : str
        Auxiliary working directory where the actual astrometric calibration
        takes place.
    cmd : instance of CmdExecute
        Auxiliary class to execute a command line.
    verbose : bool or None
       If True, display intermediate information.
    """
    basename = os.path.basename(output_fname)
    backupsubdir = basename[:-5]
    backupsubdirfull = '{}/{}'.format(nightdir, backupsubdir)
    if os.path.isdir(backupsubdirfull):
        if verbose:
            print('Subdirectory {} found'.format(backupsubdirfull))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(backupsubdirfull))
        os.makedirs(backupsubdirfull)
    tobesaved = ['astrometry-net.pdf', 'astrometry-scamp.pdf', 'astrometry.log',
                 'xxx.new', 'full_1.cat', 'merged_1.cat']
    for filename in tobesaved:
        if os.path.isfile('{}/{}'.format(workdir, filename)):
            command = 'cp {} ../{}/'.format(filename, backupsubdir)
            cmd.run(command, cwd=workdir)


def run_astrometry(image2d, mask2d, saturpix,
                   header, maxfieldview_arcmin, fieldfactor, pvalues,
                   nightdir, output_fname,
                   interactive, verbose, debug=False):
    """
    Compute astrometric solution of image.

    Note that the input parameter header is modified in output.

    Parameters
    ----------
    image2d : numpy 2D array
        Image to be calibrated.
    mask2d : numpy 2D array
        Useful region mask.
    saturpix : numpy 2D array
        Array storing the location of saturated pixels in the raw data.
    header: astropy header
        Initial header of the image prior to the astrometric
        calibration.
    maxfieldview_arcmin : float
        Maximum field of view. This is necessary to retrieve the GAIA
        data for the astrometric calibration.
    fieldfactor : float
        Multiplicative factor to enlarge the required field of view
        in order to facilitate the reuse of the downloaded GAIA data.
    pvalues : list of int
        Possible P values for build-astrometry-index (scale number)
        in the order to be employed (if one fails, the next one is used).
        See help of build-astrometry-index for details.
    nightdir : str or None
        Directory where the reduced images will be stored.
    output_fname : str or None
        Output file name.
    interactive : bool or None
        If True, enable interactive execution (e.g. plots,...).
    verbose : bool or None
        If True, display intermediate information.
    debug : bool or None
        Display additional debugging information.

    Returns
    -------
    ierr_astr : int
        Error status value. 0: no error. 1: error while performing
        astrometric calibration.
    astrsumm1 : instance of AstrSumm
        Summary of the astrometric calibration with Astronomy.net.
    astrsumm2 : instance of AstrSumm
        Summary of the astrometric calibration with AstrOmatic.net.
    """

    ierr_astr = 0
    astrsumm1 = None
    astrsumm2 = None

    # creating work subdirectory
    workdir = nightdir + '/work'

    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    else:
        filelist = glob.glob('{}/*'.format(workdir))
        if verbose:
            print('\nRemoving previous files: {}'.format(filelist))
        for filepath in filelist:
            try:
                os.remove(filepath)
            except:
                print("Error while deleting file : ", filepath)

    # define ToLogFile object
    logfile = ToLogFile(workdir=workdir, verbose=verbose)
    logfile.print('\nAstrometric calibration of {}'.format(output_fname))

    # define CmdExecute object
    cmd = CmdExecute(logfile)

    # generate myastrometry.cfg
    cfgfile = '{}/myastrometry.cfg'.format(workdir)
    with open(cfgfile, 'wt') as f:
        f.write('add_path .\nindex index-image')
        logfile.print('Creating configuration file {}'.format(cfgfile))

    # remove deprecated WCS keywords:
    for kwd in ['pc001001', 'pc001002', 'pc002001', 'pc002002']:
        if kwd in header:
            del header[kwd]
    # rename deprecated RADECSYS as RADESYS
    if 'RADECSYS' in header:
        header.rename_keyword('RADECSYS', 'RADESYS')

    # RA, DEC, and DATE-OBS from the image header
    ra_initial = header['ra']
    dec_initial = header['dec']
    dateobs = header['date-obs']
    c_fk5_dateobs = SkyCoord(ra=ra_initial * u.degree,
                             dec=dec_initial * u.degree,
                             frame='fk5', equinox=Time(dateobs))
    c_fk5_j2000 = c_fk5_dateobs.transform_to(FK5(equinox='J2000'))
    logfile.print('Central coordinates:')
    logfile.print(str(c_fk5_dateobs))
    logfile.print(str(c_fk5_j2000))
    ra_center = c_fk5_j2000.ra.deg * np.pi / 180
    dec_center = c_fk5_j2000.dec.deg * np.pi / 180
    xj2000 = np.cos(ra_center) * np.cos(dec_center)
    yj2000 = np.sin(ra_center) * np.cos(dec_center)
    zj2000 = np.sin(dec_center)

    # read JSON file with central coordinates of fields already calibrated
    jsonfname = '{}/central_pointings.json'.format(nightdir)
    if os.path.exists(jsonfname):
        with open(jsonfname) as jfile:
            ccbase = json.load(jfile)
    else:
        ccbase = dict()

    # decide whether new GAIA data is needed
    retrieve_new_gaia_data = True
    if len(ccbase) > 0:
        indexid = len(ccbase) + 1
        for i in ccbase:
            x = ccbase[i]['x']
            y = ccbase[i]['y']
            z = ccbase[i]['z']
            search_radius_arcmin = ccbase[i]['search_radius_arcmin']
            # angular distance (radians)
            dist_rad = np.arccos(x * xj2000 + y * yj2000 + z * zj2000)
            # angular distance (arcmin)
            dist_arcmin = dist_rad * 180 / np.pi * 60
            if (maxfieldview_arcmin / 2) + dist_arcmin < search_radius_arcmin:
                indexid = int(i[-6:])
                retrieve_new_gaia_data = False
                break
    else:
        indexid = 1

    # create index subdir
    subdir = 'index{:06d}'.format(indexid)
    # create path to subdir
    newsubdir = nightdir + '/' + subdir
    if not os.path.isdir(newsubdir):
        logfile.print('Subdirectory {} not found. Creating it!'.format(newsubdir))
        os.makedirs(newsubdir)

    if retrieve_new_gaia_data:
        # generate additional logfile for retrieval of GAIA data
        loggaianame = '{}/gaialog.log'.format(newsubdir)
        loggaia = open(loggaianame, 'wt')
        logfile.print('-> Creating {}'.format(loggaianame))
        loggaia.write('Querying GAIA data...\n')
        # generate query for GAIA
        search_radius_arcmin = fieldfactor * (maxfieldview_arcmin / 2)
        search_radius_degree = search_radius_arcmin / 60
        # loop in phot_g_mean_mag
        # ---
        mag_minimum = 0
        gaia_query_line, tap_result = retrieve_gaia(c_fk5_j2000.ra.deg, c_fk5_j2000.dec.deg, search_radius_degree,
                                                    mag_minimum, loggaia)
        nobjects_mag_minimum = len(tap_result)
        logfile.print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_minimum, nobjects_mag_minimum))
        if nobjects_mag_minimum >= NMAXGAIA:
            raise SystemError('Unexpected')
        # ---
        mag_maximum = 30
        gaia_query_line, tap_result = retrieve_gaia(c_fk5_j2000.ra.deg, c_fk5_j2000.dec.deg, search_radius_degree,
                                                    mag_maximum, loggaia)
        nobjects_mag_maximum = len(tap_result)
        logfile.print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_maximum, nobjects_mag_maximum))
        if nobjects_mag_maximum < NMAXGAIA:
            loop_in_gaia = False
        else:
            loop_in_gaia = True
        # ---
        niter = 0
        nitermax = 50
        while loop_in_gaia:
            niter += 1
            loggaia.write('Iteration {}\n'.format(niter))
            mag_medium = (mag_minimum + mag_maximum) / 2
            gaia_query_line, tap_result = retrieve_gaia(c_fk5_j2000.ra.deg, c_fk5_j2000.dec.deg, search_radius_degree,
                                                        mag_medium, loggaia)
            nobjects = len(tap_result)
            logfile.print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_medium, nobjects))
            if nobjects < NMAXGAIA:
                if mag_maximum - mag_minimum < 0.1:
                    loop_in_gaia = False
                else:
                    mag_minimum = mag_medium
            else:
                mag_maximum = mag_medium
            if niter > nitermax:
                loggaia.write('ERROR: nitermax reached while retrieving GAIA data')
                loop_in_gaia = False

        loggaia.write(str(tap_result.to_table()) + '\n')
        loggaia.close()

        logfile.print('Querying GAIA data: {} objects found'.format(len(tap_result)))

        # proper motion correction
        logfile.print('-> Applying proper motion correction...')
        source_id = []
        ra_corrected = []
        dec_corrected = []
        phot_g_mean_mag = []
        for irecord, record in enumerate(tap_result):
            source_id.append(record['source_id'])
            phot_g_mean_mag.append(record['phot_g_mean_mag'])
            ra, dec = record['ra'], record['dec']
            pmra, pmdec = record['pmra'], record['pmdec']
            ref_epoch = record['ref_epoch']
            if not np.isnan(pmra) and not np.isnan(pmdec):
                t0 = Time(ref_epoch, format='decimalyear')
                c = SkyCoord(ra=ra * u.degree,
                             dec=dec * u.degree,
                             pm_ra_cosdec=pmra * u.mas / u.yr,
                             pm_dec=pmdec * u.mas / u.yr,
                             obstime=t0
                             )
                dt = Time(dateobs) - t0
                c_corrected = c.apply_space_motion(dt=dt.jd * u.day)
                if debug:
                    print(irecord, ra, c_corrected.ra.value, dec, c_corrected.dec.value)
                ra_corrected.append(c_corrected.ra.value)
                dec_corrected.append(c_corrected.dec.value)
            else:
                ra_corrected.append(ra)
                dec_corrected.append(dec)

        # save GAIA objects in FITS binary table
        hdr = fits.Header()
        hdr.add_history('GAIA objets selected with following query:')
        hdr.add_history(gaia_query_line)
        hdr.add_history('---')
        hdr.add_history('Note that RA and DEC have been corrected from proper motion')
        primary_hdu = fits.PrimaryHDU(header=hdr)
        col1 = fits.Column(name='source_id', format='K', array=source_id)
        col2 = fits.Column(name='ra', format='D', array=ra_corrected)
        col3 = fits.Column(name='dec', format='D', array=dec_corrected)
        col4 = fits.Column(name='phot_g_mean_mag', format='E', array=phot_g_mean_mag)
        hdu = fits.BinTableHDU.from_columns([col1, col2, col3, col4])
        hdul = fits.HDUList([primary_hdu, hdu])
        outfname = nightdir + '/' + subdir + '/GaiaDR2-query.fits'
        hdul.writeto(outfname, overwrite=True)
        logfile.print('-> Saving {}'.format(outfname))

        # update JSON file with central coordinates of fields already calibrated
        ccbase[subdir] = {
            'ra': c_fk5_j2000.ra.degree,
            'dec': c_fk5_j2000.dec.degree,
            'x': xj2000,
            'y': yj2000,
            'z': zj2000,
            'search_radius_arcmin': search_radius_arcmin
        }
        with open(jsonfname, 'w') as outfile:
            json.dump(ccbase, outfile, indent=2)

    else:
        # copying the previously computed WCS image
        logfile.print('Reusing previously downloaded GAIA catalogue')

    command = 'cp {}/{}/GaiaDR2-query.fits {}/work/'.format(nightdir, subdir, nightdir)
    cmd.run(command)

    # image dimensions
    naxis2, naxis1 = image2d.shape

    # save temporary FITS file
    tmpfname = '{}/xxx.fits'.format(workdir)
    header.add_history('--Computing Astrometry.net WCS solution--')
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
    hdu.writeto(tmpfname, overwrite=True)
    logfile.print('\nGenerating reduced image {}/xxx.fits (after bias '
                  'subtraction and flatfielding)\n'.format(workdir))

    logfile.print('\n*** Using Astrometry.net tools ***')
    ip = 0
    loop = True
    while loop:
        # generate index file with GAIA data
        command = 'build-astrometry-index -i GaiaDR2-query.fits'
        command += ' -o index-image.fits'
        command += ' -A ra -D dec -S phot_g_mean_mag'
        command += ' -P {}'.format(pvalues[ip])
        command += ' -E -I {}'.format(indexid)
        cmd.run(command, cwd=workdir)

        # solve fieldmormo
        command = 'solve-field -p'
        command += ' --config myastrometry.cfg --overwrite'
        command += ' --ra ' + str(c_fk5_j2000.ra.degree)
        command += ' --dec ' + str(c_fk5_j2000.dec.degree)
        command += ' --radius {}'.format(maxfieldview_arcmin / 120)
        command += ' xxx.fits'
        cmd.run(command, cwd=workdir)

        # check that the field solved
        if not os.path.isfile('{}/xxx.solved'.format(workdir)):
            logfile.print('WARNING: field did not solve.')
            if ip < len(pvalues) - 1:
                logfile.print('WARNING: trying with new P value.')
                ip += 1
            else:
                ierr_astr = 1
                msg = 'Unable to solve the field with Astrometry.net'
                logfile.print(msg)
                header.add_history(msg)
                hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
                hdu.writeto(output_fname, overwrite=True)
                logfile.print('-> file {} created'.format(output_fname))
                save_auxfiles(output_fname=output_fname, nightdir=nightdir, workdir=workdir, cmd=cmd, verbose=verbose)
                logfile.close()
                return ierr_astr, astrsumm1, astrsumm2
        else:
            loop = False

    # check for saturated objects
    with fits.open('{}/xxx.axy'.format(workdir), 'update') as hdul_table:
        tbl = hdul_table[1].data
        isaturated = []
        for i in range(tbl.shape[0]):
            ix = int(tbl['X'][i] + 0.5)
            iy = int(tbl['Y'][i] + 0.5)
            if saturpix[iy - 1, ix - 1]:
                isaturated.append(i)
        logfile.print('Checking file: {}/xxx.axy'.format(workdir))
        logfile.print('Number of saturated objects found: {}/{}'.format(len(isaturated), tbl.shape[0]))
        if len(isaturated) > 0:
            for i in isaturated:
                logfile.print('Saturated object: {}'.format(tbl[i]))
        if len(isaturated) > 0:
            hdul_table[1].data = np.delete(tbl, isaturated)
            logfile.print('File: {}/xxx.axy updated\n'.format(workdir))

    if len(isaturated) > 0:
        # rerun code
        command = 'solve-field -p'
        command += ' --config myastrometry.cfg --continue'
        command += ' --width {} --height {}'.format(naxis1, naxis2)
        command += ' --x-column X --y-column Y --sort-column FLUX'
        command += ' --ra ' + str(c_fk5_j2000.ra.degree)
        command += ' --dec ' + str(c_fk5_j2000.dec.degree)
        command += ' --radius {}'.format(maxfieldview_arcmin / 120)
        command += ' xxx.axy'
        cmd.run(command, cwd=workdir)

        # check that the field solved
        if not os.path.isfile('{}/xxx.solved'.format(workdir)):
            ierr_astr = 1
            msg = 'Unable to solve the field with Astrometry.net'
            logfile.print(msg)
            header.add_history(msg)
            hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
            hdu.writeto(output_fname, overwrite=True)
            logfile.print('-> file {} created'.format(output_fname))
            save_auxfiles(output_fname=output_fname, nightdir=nightdir, workdir=workdir, cmd=cmd, verbose=verbose)
            logfile.close()
            return ierr_astr, astrsumm1, astrsumm2

        # insert new WCS into image header
        command = 'new-wcs -i xxx.fits -w xxx.wcs -o xxx.new -d'
        cmd.run(command, cwd=workdir)

    # read GaiaDR2 table and convert RA, DEC to X, Y
    # (note: the same result can be accomplished using the command-line program:
    # $ wcs-rd2xy -w xxx.wcs -i GaiaDR2-query.fits -o gaia-xy.fits)
    with fits.open('{}/GaiaDR2-query.fits'.format(workdir)) as hdul_table:
        gaiadr2 = hdul_table[1].data
    with fits.open('{}/xxx.new'.format(workdir)) as hdul:
        w = WCS(hdul[0].header)
    xgaia, ygaia = w.all_world2pix(gaiadr2.ra, gaiadr2.dec, 1)
    # compute pixel scale (mean in both axis) in arcsec/pix
    pixel_scales_arcsec_pix = proj_plane_pixel_scales(w)*3600
    logfile.print('astrometry.net> pixel scales (arcsec/pix): {}'.format(pixel_scales_arcsec_pix))

    # load corr file
    corrfname = '{}/xxx.corr'.format(workdir)
    with fits.open(corrfname) as hdul_table:
        tcorr = hdul_table[1].data

    # generate plots
    astrsumm1 = plot_astrometry(
        output_fname=output_fname,
        image2d=image2d,
        mask2d=mask2d,
        peak_x=tcorr.field_x, peak_y=tcorr.field_y,
        pred_x=tcorr.index_x, pred_y=tcorr.index_y,
        xcatag=xgaia, ycatag=ygaia,
        pixel_scales_arcsec_pix=pixel_scales_arcsec_pix,
        workdir=workdir,
        interactive=interactive, logfile=logfile,
        suffix='net'
    )

    # open result and update header
    result_fname = '{}/xxx.new'.format(workdir)
    with fits.open(result_fname) as hdul:
        newheader = hdul[0].header

    # copy configuration files for astrometric.net
    logfile.print('\n*** Using AstrOmatic.net tools ***')
    conffiles = ['default.param', 'config.sex', 'config.scamp']
    for fname in conffiles:
        dumdata = pkgutil.get_data('filabres.astromatic', fname)
        txtfname = '{}/{}'.format(workdir, fname)
        logfile.print('Generating {}'.format(txtfname))
        with open(txtfname, 'wt') as f:
            f.write(str(dumdata.decode('utf8')))
    if verbose:
        logfile.print(' ')

    # run sextractor
    command = 'sex xxx.new -c config.sex -CATALOG_NAME xxx.ldac'
    cmd.run(command, cwd=workdir)

    # run scamp
    command = 'scamp xxx.ldac -c config.scamp'
    cmd.run(command, cwd=workdir)

    # check there is a useful result
    if os.path.exists('{}/xxx.head'.format(workdir)):
        with open('{}/xxx.head'.format(workdir)) as fdum:
            singleline = fdum.read()
        if 'PV2_10' not in singleline:
            ierr_astr = 2
    else:
        ierr_astr = 2
    if ierr_astr == 2:
        msg = 'Unable to solve the field with AstrOmatic.net'
        logfile.print(msg)
        newheader.add_history(msg)
        newheader['history'] = '-------------------------------------------------------'
        newheader['history'] = 'Summary of astrometric calibration with Astrometry.net:'
        newheader['history'] = '- pixscale: {}'.format(astrsumm1.pixscale)
        newheader['history'] = '- ntargets: {}'.format(astrsumm1.ntargets)
        newheader['history'] = '- meanerr: {}'.format(astrsumm1.meanerr)
        newheader['history'] = '-------------------------------------------------------'
        hdu = fits.PrimaryHDU(image2d.astype(np.float32), newheader)
        hdu.writeto(output_fname, overwrite=True)
        logfile.print('-> file {} created'.format(output_fname))
        save_auxfiles(output_fname=output_fname, nightdir=nightdir, workdir=workdir, cmd=cmd, verbose=verbose)
        logfile.close()
        return ierr_astr, astrsumm1, astrsumm2

    # remove SIP parameters in newheader
    newheader['history'] = '--Deleting SIP from Astrometry.net WCS solution--'
    newheader.add_comment('--Deleted SIP from Astrometry.net WCS solution--')
    sip_param = []
    for p in ['', 'P']:
        for c in ['A', 'B']:
            sip_param += ['{}{}_ORDER'.format(c, p)]
            sip_param += ['{}{}_{}_{}'.format(c, p, i, j) for i in range(3) for j in range(3) if i + j < 3]
    for kwd in sip_param:
        kwd_value = newheader[kwd]
        kwd_comment = newheader.comments[kwd]
        newheader['comment'] = 'deleted {:8} = {:20} / {}'.format(kwd, kwd_value, kwd_comment)
        del newheader[kwd]
    # remove HISTORY and COMMENT entries from astrometry.net
    with fits.open('{}/xxx.wcs'.format(workdir)) as hdul:
        oldheader = hdul[0].header
    for kwd in ['HISTORY', 'COMMENT']:
        for itemval in oldheader[kwd]:
            try:
                idel = list(newheader.values()).index(itemval)
            except ValueError:
                idel = -1
            if idel > -1:
                del newheader[idel]
    # delete additional comment lines
    tobedeleted = ['Original key: "END"',
                   '--Start of Astrometry.net WCS solution--',
                   '--Put in by the new-wcs program--',
                   '--End of Astrometry.net WCS--',
                   '--(Put in by the new-wcs program)--']
    for item in tobedeleted:
        try:
            idel = list(newheader.values()).index(item)
        except ValueError:
            idel = -1
        if idel > -1:
            del newheader[idel]
    # remove blank COMMENTS
    idel = 0
    while idel > -1:
        try:
            idel = list(newheader.values()).index('')
        except ValueError:
            idel = -1
        if idel > -1:
            del newheader[idel]

    # set the TPV solution obtained with sextractor+scamp
    newheader['history'] = '--Computing new solution with SEXTRACTOR+SCAMP--'
    with open('{}/xxx.head'.format(workdir)) as tpvfile:
        tpvheader = tpvfile.readlines()
    for line in tpvheader:
        kwd = line[:8].strip()
        if kwd.find('END') > -1:
            break
        if kwd == 'COMMENT':
            pass  # Avoid problem with non-standard ASCII characters
        elif kwd == 'HISTORY':
            newheader[kwd] = line[10:].rstrip()
        else:
            # note the blank spaces to avoid problem with "S/N"
            kwd_value, kwd_comment = line[11:].split(' / ')
            try:
                value = float(kwd_value.replace('\'', ' '))
            except ValueError:
                value = kwd_value.replace('\'', ' ')
            newheader[kwd] = (value, kwd_comment.rstrip())

    # set CTYPE1 and CTYPE2 from 'RA---TAN' and 'DEC--TAN' to 'RA---TPV' and 'DEC--TPV'
    newheader['CTYPE1'] = 'RA---TPV'
    newheader['CTYPE2'] = 'DEC--TPV'

    # load WCS computed with SCAMP
    w = WCS(newheader)
    # compute pixel scale (mean in both axis) in arcsec/pix
    pixel_scales_arcsec_pix = proj_plane_pixel_scales(w)*3600
    logfile.print('astrometry> pixel scales (arcsec/pix): {}'.format(pixel_scales_arcsec_pix))

    # load peak location from catalogue
    peak_x, peak_y = load_scamp_cat('full', workdir, logfile)
    peak_ra, peak_dec = load_scamp_cat('merged', workdir, logfile)
    pred_x, pred_y = w.wcs_world2pix(peak_ra, peak_dec, 1)

    # predict expected location of GAIA data
    with fits.open('{}/GaiaDR2-query.fits'.format(workdir)) as hdul_table:
        gaiadr2 = hdul_table[1].data
    xgaia, ygaia = w.wcs_world2pix(gaiadr2.ra, gaiadr2.dec, 1)

    # generate plots
    astrsumm2 = plot_astrometry(
        output_fname=output_fname,
        image2d=image2d,
        mask2d=mask2d,
        peak_x=peak_x, peak_y=peak_y,
        pred_x=pred_x, pred_y=pred_y,
        xcatag=xgaia, ycatag=ygaia,
        pixel_scales_arcsec_pix=pixel_scales_arcsec_pix,
        workdir=workdir,
        interactive=interactive, logfile=logfile,
        suffix='scamp'
    )

    # store astrometric summaries in history
    newheader['history'] = '-------------------------------------------------------'
    newheader['history'] = 'Summary of astrometric calibration with Astrometry.net:'
    newheader['history'] = '- pixscale: {}'.format(astrsumm1.pixscale)
    newheader['history'] = '- ntargets: {}'.format(astrsumm1.ntargets)
    newheader['history'] = '- meanerr: {}'.format(astrsumm1.meanerr)
    newheader['history'] = '-------------------------------------------------------'
    newheader['history'] = 'Summary of astrometric calibration with AstrOmatic.net:'
    newheader['history'] = '- pixscale: {}'.format(astrsumm2.pixscale)
    newheader['history'] = '- ntargets: {}'.format(astrsumm2.ntargets)
    newheader['history'] = '- meanerr: {}'.format(astrsumm2.meanerr)
    newheader['history'] = '-------------------------------------------------------'

    # save result
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), newheader)
    hdu.writeto(output_fname, overwrite=True)
    logfile.print('-> file {} created'.format(output_fname))

    # close logfile
    logfile.close()

    # storing relevant files in corresponding subdirectory
    save_auxfiles(output_fname=output_fname, nightdir=nightdir, workdir=workdir, cmd=cmd, verbose=verbose)

    return ierr_astr, astrsumm1, astrsumm2
