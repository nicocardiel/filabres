from astropy import units as u
from astropy.coordinates import SkyCoord, FK5
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import glob
import json
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import os
import pkgutil
import pyvo
import re
import subprocess

from .ximshow import ximshow
from .pause_debugplot import pause_debugplot

NMAXGAIA = 2000


class ToLogFile:
    def __init__(self, workdir, verbose):
        self.filename = '{}/astrometry.log'.format(workdir)
        self.logfile = open(self.filename, 'wt')
        self.verbose = verbose

    def print(self, line):
        if self.verbose:
            print(line)
        if not self.logfile.closed:
            self.logfile.write(line + '\n')

    def close(self):
        self.logfile.close()


class CmdExecute:
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


def retrieve_gaia(ra_deg, dec_deg, radius_deg, magnitude, loggaia):
    """
    Retrieve GAIA data.

    Cone search around ra_deg, dec_deg, within a radius given by
    radius_deg, and within a given limiting magnitude.

    Parameters
    ==========
    ra_deg : float
        Right ascension of the central point.
    dec_deg : float
        Declination of the central point.
    radius_deg : float
        Radius of the cone search.
    magnitude : float
        Limiting magnitude.
    loggaia : file handler
        Log file to store intermediate results.

    Returns
    =======
    gaia_query_line : str
        Full query.
    tap_result : TAPResults instance
        Result of the cone search
    """
    gaia_query_line1 = 'SELECT TOP {} source_id, ref_epoch, ' \
                       'ra, ra_error, dec, dec_error, ' \
                       'parallax, parallax_error, ' \
                       'pmra, pmra_error, pmdec, pmdec_error, ' \
                       'phot_g_mean_mag, bp_rp, ' \
                       'radial_velocity, radial_velocity_error, ' \
                       'a_g_val'.format(NMAXGAIA)
    gaia_query_line2 = 'FROM gdr2.gaia_source'
    gaia_query_line3 = '''WHERE CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec), ''' + \
                       '''CIRCLE('ICRS',''' + \
                       '{},{},{}'.format(ra_deg, dec_deg, radius_deg) + \
                       '))=1'
    gaia_query_line4 = 'AND phot_g_mean_mag < {}'.format(magnitude)
    gaia_query_line = gaia_query_line1 + ' ' + gaia_query_line2 + ' ' + gaia_query_line3 + ' ' + gaia_query_line4

    loggaia.write('Querying GAIA data with phot_g_mean_mag={:.2f}\n'.format(magnitude))

    loggaia.write(gaia_query_line + '\n')
    # retrieve GAIA data using the Table Access Protocol;
    # see specific details for retrieval of GAIA data in
    # https://gaia.aip.de/cms/documentation/tap-interface/
    tap_service = pyvo.dal.TAPService('https://gaia.aip.de/tap')
    tap_result = tap_service.run_sync(gaia_query_line)
    return gaia_query_line, tap_result


def plot_astrometry(output_filename, image2d,
                    peak_x, peak_y, pred_x, pred_y, xcatag, ycatag,
                    pixel_scales_arcsec_pix, workdir, interactive, logfile,
                    suffix):
    """
    Generate plots with the results of the astrometric calibration.

    Parameters
    ==========
    output_filename : str or None
        Output file name.
    image2d : numpy 2D array
        Image to be calibrated.
    peak_x : numpy 1D array
        Measured X coordinate of the detected objects.
    peak_y : numpy 1D array
        Measured Y coordinate of the detected objects.
    pred_x : numpy 1D array
        X coordinate of the detected objects predicted by the
        astrometric calibration.
    pred_y : numpy 1D array
        X coordinate of the detected objects predicted by the
        astrometric calibration.
    xcatag : numpy 1D array
        X coordinate of the full catalog of objects as
        predicted by the astrometric calibration.
    ycatag : numpy 1D array
        X coordinate of the full catalog of objects as
        predicted by the astrometric calibration.
    pixel_scales_arcsec_pix : numpy 1D array
        X and Y pixel scales, in arcsec/pix.
    workdir : str
        Work subdirectory.
    interactive : bool or None
        If True, enable interactive execution (e.g. plots,...).
    logfile : ToLogFile instance
        Log file where the astrometric calibration information is
        stored.
    suffix : str
        Suffix to be appended to PDF output.
    """

    ntargets = len(peak_x)
    naxis2, naxis1 = image2d.shape

    mean_pixel_scale_arcsec_pix = np.mean(pixel_scales_arcsec_pix)
    delta_x = (pred_x - peak_x) * mean_pixel_scale_arcsec_pix
    delta_y = (pred_y - peak_y) * mean_pixel_scale_arcsec_pix
    delta_r = np.sqrt(delta_x * delta_x + delta_y * delta_y)
    rorder = np.argsort(delta_r)
    meanerr = np.mean(delta_r)
    logfile.print('astrometry-{}> Number of targest found: {}'.format(suffix, ntargets))
    logfile.print('astrometry-{}> Mean error (arcsec)....: {}'.format(suffix, meanerr))
    for i, iorder in enumerate(rorder):
        if delta_r[iorder] > 3 * meanerr:
            logfile.print('-> outlier point #{}, delta_r (arcsec): {}'.format(i+1, delta_r[iorder]))

    plot_suptitle = '[File: {}]'.format(os.path.basename(output_filename))
    plot_title = 'astrometry-{} (npoints={}, meanerr={:.3f} arcsec)'.format(suffix, ntargets, meanerr)
    # plot 1: X and Y errors
    pp = PdfPages('{}/astrometry-{}.pdf'.format(workdir, suffix))
    fig, ax = plt.subplots(1, 1, figsize=(11.7, 8.3))
    fig.suptitle(plot_suptitle)
    ax.plot(delta_x, delta_y, 'mo', alpha=0.5)
    rmax = 2.0  # arcsec
    for i, iorder in enumerate(rorder):
        if abs(delta_x[iorder]) < rmax and abs(delta_y[iorder]) < rmax:
            ax.text(delta_x[iorder], delta_y[iorder], str(i+1), fontsize=15)
    circle1 = plt.Circle((0, 0), 0.5, color='b', fill=False)
    circle2 = plt.Circle((0, 0), 1.0, color='g', fill=False)
    circle3 = plt.Circle((0, 0), 1.5, color='r', fill=False)
    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(circle3)
    ax.set_xlim([-rmax, rmax])
    ax.set_ylim([-rmax, rmax])
    ax.set_xlabel('delta X (arcsec): predicted - peak')
    ax.set_ylabel('delta Y (arcsec): predicted - peak')
    ax.set_title(plot_title)
    ax.set_aspect('equal', 'box')
    pp.savefig()
    if interactive:
        plt.show()
    # plots 2 and 3: histograms with deviations in the X and Y axis
    for iplot in [1, 2]:
        fig, ax = plt.subplots(1, 1, figsize=(11.7, 8.3))
        fig.suptitle(plot_suptitle)
        if iplot == 1:
            ax.hist(delta_x, 30)
            ax.set_xlabel('delta X (arcsec): predicted - peak')
        else:
            ax.hist(delta_y, 30)
            ax.set_xlabel('delta Y (arcsec): predicted - peak')
        ax.set_ylabel('Number of targets')
        ax.set_title(plot_title)
        pp.savefig()
        if interactive:
            plt.show()
    # plot 3: image with identified objects
    ax = ximshow(image2d, cmap='gray', show=False, figuredict={'figsize': (11.7, 8.3)},
                 title=plot_title, tight_layout=False)
    ax.plot(peak_x, peak_y, 'bo', fillstyle='none', markersize=10, label='peaks')
    for i, iorder in enumerate(rorder):
        ax.text(peak_x[iorder], peak_y[iorder], str(i + 1), fontsize=15, color='blue')
    ax.plot(xcatag, ycatag, 'mx', alpha=0.2, markersize=10, label='predicted_gaiacat')
    ax.plot(pred_x, pred_y, 'g+', markersize=10, label='predicted_peaks')
    ax.set_xlim([min(np.min(xcatag), -0.5), max(np.max(xcatag), naxis1 + 0.5)])
    ax.set_ylim([min(np.min(ycatag), -0.5), max(np.max(ycatag), naxis2 + 0.5)])
    ax.legend()
    plt.suptitle(plot_suptitle)
    pp.savefig()
    if interactive:
        pause_debugplot(debugplot=12, pltshow=True, tight_layout=False)
    pp.close()
    plt.close()


def load_scamp_cat(catalogue, workdir, verbose):
    """
    Load X, Y coordinates from catalogue generated with SCAMP

    Parameters
    ==========
    catalogue : str
        Catalogue to be read. It must be 'full' or 'merged'.
    workdir : str
        Work subdirectory.
    verbose : bool or None
        If True, display intermediate information.

    Returns
    =======
    col1, col2 : numpy 1D arrays
        X, Y coordinates of the peaks (only if catalogue is 'full').
        RA, DEC coordinates of the peaks (only if catalogue is 'merged').
    """

    if catalogue not in ['full', 'merged']:
        msg = 'Invalid catalogue description: {}'.format(catalogue)
        raise SystemError(msg)

    filename = '{}/{}_1.cat'.format(workdir, catalogue)
    with open(filename, 'rt') as f:
        fulltxt = f.readlines()

    if verbose:
        print('Reading {}'.format(filename))

    # determine relevant column numbers
    if catalogue == 'full':
        colnames = ['X_IMAGE', 'Y_IMAGE', 'CATALOG_NUMBER']
    else:
        colnames = ['ALPHA_J2000', 'DELTA_J2000']
    ncol = []
    for col in colnames:
        ii = None
        for i, line in enumerate(fulltxt):
            if col in line:
                ii = i + 1
                break
        if ii is None:
            msg = '{} not found in {}'.format(col, filename)
            raise SystemError(msg)
        if verbose:
            print('{} is located in column #{}'.format(col, ii))
        ncol.append(ii - 1)

    # read full data set
    fulltable = np.genfromtxt(filename)

    if catalogue == 'full':
        # delete invalid rows (those with CATALOG_NUMBER == 0)
        valid_rows = np.where(fulltable[:, ncol[2]] != 0)[0]
        if verbose:
            print('Number of objects read: {}'.format(len(valid_rows)))
        newtable = fulltable[valid_rows, :]
    else:
        newtable = fulltable

    col1 = newtable[:, ncol[0]]
    col2 = newtable[:, ncol[1]]

    return col1, col2


def run_astrometry(image2d, mask2d, saturpix,
                   header, maxfieldview_arcmin, fieldfactor,
                   nightdir, output_filename,
                   interactive, verbose, debug=False):
    """
    Compute astrometric solution of image.

    Note that the input parameter header is modified in output.

    Parameters
    ==========
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
    nightdir : str or None
        Directory where the raw image is stored and the auxiliary
        images created by run_astrometry will be placed.
    output_filename : str or None
        Output file name.
    interactive : bool or None
        If True, enable interactive execution (e.g. plots,...).
    verbose : bool or None
        If True, display intermediate information.
    debug : bool or None
        Display additional debugging information.

    Returns
    =======
    ierr_astr : int
        Error status value. 0: no error. 1: error while performing
        astrometric calibration.
    """

    ierr_astr = 0

    # creating work subdirectory
    workdir = nightdir + '/work'

    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    else:
        filelist = glob.glob('{}/*'.format(workdir))
        print('\nRemoving previous files: {}'.format(filelist))
        for filepath in filelist:
            try:
                os.remove(filepath)
            except:
                print("Error while deleting file : ", filepath)

    # define ToLogFile object
    logfile = ToLogFile(workdir=workdir, verbose=verbose)
    logfile.print('\nAstrometric calibration of {}'.format(output_filename))

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
    jsonfilename = '{}/central_pointings.json'.format(nightdir)
    if os.path.exists(jsonfilename):
        with open(jsonfilename) as jfile:
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
        if verbose:
            print('-> Creating {}'.format(loggaianame))
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
        if verbose:
            print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_minimum, nobjects_mag_minimum))
        if nobjects_mag_minimum >= NMAXGAIA:
            raise SystemError('Unexpected')
        # ---
        mag_maximum = 30
        gaia_query_line, tap_result = retrieve_gaia(c_fk5_j2000.ra.deg, c_fk5_j2000.dec.deg, search_radius_degree,
                                                    mag_maximum, loggaia)
        nobjects_mag_maximum = len(tap_result)
        if verbose:
            print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_maximum, nobjects_mag_maximum))
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
            if verbose:
                print('-> Gaia data: magnitude, nobjects: {:.3f}, {}'.format(mag_medium, nobjects))
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

        if verbose:
            print('Querying GAIA data: {} objects found'.format(len(tap_result)))

        # proper motion correction
        if verbose:
            print('-> Applying proper motion correction...')
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
        outfilename = nightdir + '/' + subdir + '/GaiaDR2-query.fits'
        hdul.writeto(outfilename, overwrite=True)
        if verbose:
            print('-> Saving {}'.format(outfilename))

        # generate index file with GAIA data
        command = 'build-astrometry-index -i {}/{}/GaiaDR2-query.fits'.format(nightdir, subdir)
        command += ' -o {}/{}/index-image.fits'.format(nightdir, subdir)
        command += ' -A ra -D dec -S phot_g_mean_mag'
        pvalue = int((np.log(maxfieldview_arcmin)-np.log(6))/np.log(np.sqrt(2)) + 0.5)
        if pvalue < 0:
            pvalue = 0
        elif pvalue > 19:
            pvalue = 19
        command += ' -P {}'.format(pvalue)
        command += ' -E -I {}'.format(indexid)
        cmd.run(command)

        # update JSON file with central coordinates of fields already calibrated
        ccbase[subdir] = {
            'ra': c_fk5_j2000.ra.degree,
            'dec': c_fk5_j2000.dec.degree,
            'x': xj2000,
            'y': yj2000,
            'z': zj2000,
            'search_radius_arcmin': search_radius_arcmin
        }
        with open(jsonfilename, 'w') as outfile:
            json.dump(ccbase, outfile, indent=2)

    else:
        # copying the previously computed WCS image
        logfile.print('Reusing previously downloaded GAIA catalogue and index')

    command = 'cp {}/{}/GaiaDR2-query.fits {}/work/'.format(nightdir, subdir, nightdir)
    cmd.run(command)

    command = 'cp {}/{}/index-image.fits {}/work/'.format(nightdir, subdir, nightdir)
    cmd.run(command)

    # image dimensions
    naxis2, naxis1 = image2d.shape

    # save temporary FITS file
    tmpfilename = '{}/xxx.fits'.format(workdir)
    header.add_history('--Computing Astrometry.net WCS solution--')
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
    hdu.writeto(tmpfilename, overwrite=True)

    # solve field
    command = 'solve-field -p'
    command += ' --config myastrometry.cfg --overwrite'.format(newsubdir)
    command += ' --ra ' + str(c_fk5_j2000.ra.degree)
    command += ' --dec ' + str(c_fk5_j2000.dec.degree)
    command += ' --radius {}'.format(maxfieldview_arcmin / 120)
    command += ' xxx.fits'
    cmd.run(command, cwd=workdir)

    # check for saturated objects
    with fits.open('{}/xxx.axy'.format(workdir), 'update') as hdul_table:
        tbl = hdul_table[1].data
        isaturated = []
        for i in range(tbl.shape[0]):
            ix = int(tbl['X'][i] + 0.5)
            iy = int(tbl['Y'][i] + 0.5)
            if saturpix[iy, ix]:
                isaturated.append(i)
        if len(isaturated) > 0:
            if verbose:
                print('Number of saturated objects found: {}/{}'.format(len(isaturated), tbl.shape[0]))
                for i in isaturated:
                    print('Saturated object: {}'.format(tbl[i]))
            hdul_table[1].data = np.delete(tbl, isaturated)

    if len(isaturated) > 0:
        # rerun code
        command = 'solve-field -p'
        command += ' --config myastrometry.cfg --continue'.format(newsubdir)
        command += ' --width {} --height {}'.format(naxis1, naxis2)
        command += ' --x-column X --y-column Y --sort-column FLUX'
        command += ' --ra ' + str(c_fk5_j2000.ra.degree)
        command += ' --dec ' + str(c_fk5_j2000.dec.degree)
        command += ' --radius {}'.format(maxfieldview_arcmin / 120)
        command += ' xxx.axy'
        cmd.run(command, cwd=workdir)
        # insert new WCS into image header
        command = 'new-wcs -i xxx.fits -w xxx.wcs -o xxx.new -d'
        cmd.run(command, cwd=workdir)

    # read GaiaDR2 table and convert RA, DEC to X, Y
    # (note: the same result can be accomplished using the command-line program:
    # $ wcs-rd2xy -w xxx.wcs -i GaiaDR2-query.fits -o gaia-xy.fits)
    with fits.open('{}/GaiaDR2-query.fits'.format(workdir)) as hdul_table:
        gaiadr2 = hdul_table[1].data
    w = WCS('{}/xxx.wcs'.format(workdir))
    xgaia, ygaia = w.all_world2pix(gaiadr2.ra, gaiadr2.dec, 1)
    # compute pixel scale (mean in both axis) in arcsec/pix
    pixel_scales_arcsec_pix = proj_plane_pixel_scales(w)*3600
    logfile.print('astrometry.net> pixel scales (arcsec/pix): {}'.format(pixel_scales_arcsec_pix))

    # load corr file
    corrfilename = '{}/xxx.corr'.format(workdir)
    with fits.open(corrfilename) as hdul_table:
        tcorr = hdul_table[1].data

    # generate plots
    plot_astrometry(
        output_filename=output_filename,
        image2d=image2d,
        peak_x=tcorr.field_x, peak_y=tcorr.field_y,
        pred_x=tcorr.index_x, pred_y=tcorr.index_y,
        xcatag=xgaia, ycatag=ygaia,
        pixel_scales_arcsec_pix=pixel_scales_arcsec_pix,
        workdir=workdir,
        interactive=interactive, logfile=logfile,
        suffix='net'
    )

    # open result and update header
    result_filename = '{}/xxx.new'.format(workdir)
    with fits.open(result_filename) as hdul:
        newheader = hdul[0].header

    # copy configuration files for astrometric
    conffiles = ['default.param', 'config.sex', 'config.scamp']
    for filename in conffiles:
        dumdata = pkgutil.get_data('filabres.astromatic', filename)
        txtfilename = '{}/{}'.format(workdir, filename)
        logfile.print('Generating {}'.format(txtfilename))
        with open(txtfilename, 'wt') as f:
            f.write(str(dumdata.decode('utf8')))

    # run sextractor
    command = 'sex xxx.new -c config.sex -CATALOG_NAME xxx.ldac'
    cmd.run(command, cwd=workdir)

    # run scamp
    command = 'scamp xxx.ldac -c config.scamp'
    cmd.run(command, cwd=workdir)

    # check there is a useful result
    if os.path.exists('{}/xxx.head'.format(workdir)):
        pass
    else:
        ierr_astr = 1
        return

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

    # if RADECSYS present, delete it (RADESYS has been set by SCAMP)
    if 'RADECSYS' in newheader:
        del newheader['RADECSYS']

    # set CTYPE1 and CTYPE2 from 'RA---TAN' and 'DEC--TAN' to 'RA---TPV' and 'DEC--TPV'
    newheader['CTYPE1'] = 'RA---TPV'
    newheader['CTYPE2'] = 'DEC--TPV'

    # save result
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), newheader)
    hdu.writeto(output_filename, overwrite=True)
    if verbose:
        print('-> file {} created'.format(output_filename))

    # load WCS computed with SCAMP
    w = WCS(output_filename)
    # compute pixel scale (mean in both axis) in arcsec/pix
    pixel_scales_arcsec_pix = proj_plane_pixel_scales(w)*3600
    logfile.print('astrometry> pixel scales (arcsec/pix): {}'.format(pixel_scales_arcsec_pix))

    # load peak location from catalogue
    peak_x, peak_y = load_scamp_cat('full', workdir, verbose)
    peak_ra, peak_dec = load_scamp_cat('merged', workdir, verbose)
    pred_x, pred_y = w.wcs_world2pix(peak_ra, peak_dec, 1)

    # predict expected location of GAIA data
    with fits.open('{}/GaiaDR2-query.fits'.format(workdir)) as hdul_table:
        gaiadr2 = hdul_table[1].data
    xgaia, ygaia = w.wcs_world2pix(gaiadr2.ra, gaiadr2.dec, 1)

    # generate plots
    plot_astrometry(
        output_filename=output_filename,
        image2d=image2d,
        peak_x=peak_x, peak_y=peak_y,
        pred_x=pred_x, pred_y=pred_y,
        xcatag=xgaia, ycatag=ygaia,
        pixel_scales_arcsec_pix=pixel_scales_arcsec_pix,
        workdir=workdir,
        interactive=interactive, logfile=logfile,
        suffix='scamp'
    )

    # close logfile
    logfile.close()

    # storing relevant files in corresponding subdirectory
    basename = os.path.basename(output_filename)
    backupsubdir = basename[:-5]
    backupsubdirfull = '{}/{}'.format(nightdir, backupsubdir)
    if os.path.isdir(backupsubdirfull):
        if verbose:
            print('Subdirectory {} found'.format(backupsubdirfull))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(backupsubdirfull))
        os.makedirs(backupsubdirfull)
    tobesaved = ['astrometry-net.pdf', 'astrometry-scamp.pdf', 'astrometry.log', 'xxx.new']
    for filepath in tobesaved:
        command = 'cp {} ../{}/'.format(filepath, backupsubdir)
        cmd.run(command, cwd=workdir)

    return ierr_astr