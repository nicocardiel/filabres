from astropy import units as u
from astropy.coordinates import SkyCoord, FK5
from astropy.io import fits
from astropy.time import Time
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pyvo
import subprocess

NMAXGAIA = 2000


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


def astrometry(image2d, header, maxfieldview_arcmin, fieldfactor,
               nightdir, output_filename,
               interactive, verbose, debug=False):
    """
    Compute astrometric solution of image.

    Note that the input parameter header is modified in output.

    Parameters
    ==========
    image2d : numpy 2D array
        Image to be calibrated.
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
        images created by astrometry will be placed.
    output_filename : str or None
        Output file name.
    interactive : bool or None
        If True, enable interactive execution (e.g. plots,...).
    verbose : bool or None
        If True, display intermediate information.
    debug : bool or None
        Display additional debugging information.
    """

    if verbose:
        print('\nPerforming astrometric calibration')

    # creating work subdirectory
    workdir = nightdir + '/work'
    if os.path.isdir(workdir):
        if verbose:
            print('Subdirectory {} found'.format(workdir))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(workdir))
        os.makedirs(workdir)
        # generate myastrometry.cfg
        cfgfile = '{}/myastrometry.cfg'.format(workdir)
        with open(cfgfile, 'wt') as f:
            f.write('add_path .\nindex index-image')
            if verbose:
                print('Creating configuration file {}'.format(cfgfile))

    # define and open logfile
    logfilename = '{}/astrometry.log'.format(workdir)
    logfile = open(logfilename, 'wt')
    if verbose:
        print('-> Creating {}'.format(logfilename))

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
    logfile.write('Central coordinates:\n')
    logfile.write(str(c_fk5_dateobs) + '\n')
    logfile.write(str(c_fk5_j2000) + '\n')
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
            if maxfieldview_arcmin + dist_arcmin < search_radius_arcmin:
                indexid = int(i[-6:])
                retrieve_new_gaia_data = False
                break
    else:
        indexid = 1

    # create index subdir
    subdir = 'index{:06d}'.format(indexid)
    # create path to subdir
    newsubdir = nightdir + '/' + subdir
    if os.path.isdir(newsubdir):
        if verbose:
            print('Subdirectory {} found'.format(newsubdir))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(newsubdir))
        os.makedirs(newsubdir)

    if retrieve_new_gaia_data:
        # generate additional logfile for retrieval of GAIA data
        loggaianame = '{}/gaialog.log'.format(newsubdir)
        loggaia = open(loggaianame, 'wt')
        if verbose:
            print('-> Creating {}'.format(loggaianame))
        loggaia.write('Querying GAIA data...\n')
        # generate query for GAIA
        search_radius_arcmin = fieldfactor * maxfieldview_arcmin
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
            raise SystemError('Unexpected')
        # ---
        loop_in_gaia = True
        niter = 0
        nitermax = 50
        tap_result = None  # avoid PyCharm warning
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
        if verbose:
            print('$ {}'.format(command))
        logfile.write('$ {}\n'.format(command))
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
        pout = p.stdout.read().decode('utf-8')
        p.stdout.close()
        logfile.write(pout + '\n')

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
        msg = 'Reusing previously computed index file {}/index-image.fits'.format(subdir)
        logfile.write(msg + '\n')
        if verbose:
            print('-> {}'.format(msg))

    command = 'cp {}/{}/GaiaDR2-query.fits {}/work/'.format(nightdir, subdir, nightdir)
    if verbose:
        print('$ {}'.format(command))
    logfile.write('$ {}\n'.format(command))
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    pout = p.stdout.read().decode('utf-8')
    p.stdout.close()
    logfile.write(pout + '\n')

    command = 'cp {}/{}/index-image.fits {}/work/'.format(nightdir, subdir, nightdir)
    if verbose:
        print('$ {}'.format(command))
    logfile.write('$ {}\n'.format(command))
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    pout = p.stdout.read().decode('utf-8')
    p.stdout.close()
    logfile.write(pout + '\n')

    # save temporary FITS file
    tmpfilename = '{}/xxx.fits'.format(workdir)
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
    hdu.writeto(tmpfilename, overwrite=True)

    # solve field
    # ToDo: pensar en como evitar detectar objetos espureos fuera del campo de vision
    command = 'cd {}\n'.format(workdir)
    command += 'solve-field -l 300'
    command += ' --config myastrometry.cfg --overwrite'.format(newsubdir)
    command += ' --ra ' + str(c_fk5_j2000.ra.degree)
    command += ' --dec ' + str(c_fk5_j2000.dec.degree)
    command += ' --radius 1 xxx.fits'.format(nightdir)
    if verbose:
        print('$ {}'.format(command))
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    pout = p.stdout.read().decode('utf-8')
    p.stdout.close()
    logfile.write(pout + '\n')

    # load corr file
    corrfilename = '{}/xxx.corr'.format(workdir)
    with fits.open(corrfilename) as hdul_table:
        tbl_header = hdul_table[1].header
        tbl = hdul_table[1].data
    ntargets = tbl.shape[0]
    medianerr = np.sqrt(np.median((tbl.index_x - tbl.field_x)**2 + (tbl.index_y - tbl.field_y)**2))
    if verbose:
        print('Number of targest found: {}'.format(ntargets))
        print('Median error (arcsec)..: {}'.format(medianerr))
    logfile.write('Median error (arcsec): {}\n'.format(medianerr))
    if interactive:
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        bgnd = np.median(tbl.BACKGROUND)
        naxis2, naxis1 = image2d.shape
        im_show = ax.imshow(image2d, cmap="hot", aspect='equal', vmin=0.5*bgnd, vmax=2*bgnd,
                            interpolation='nearest', origin='low', extent=[0.5, naxis1 + 0.5, 0.5, naxis2 + 0.5])

        ax.grid(False)
        for i in range(ntargets):
            if i == 0:
                label = 'field'
            else:
                label = None
            ax.plot(tbl.field_x[i], tbl.field_y[i], 'bo',
                    fillstyle='none', markersize=np.log(tbl.FLUX[i] / 5), label=label)
            if i == 0:
                label = 'index'
            else:
                label = None
            ax.plot(tbl.index_x[i], tbl.index_y[i], 'g+',
                    fillstyle='none', markersize=np.log(tbl.FLUX[i] / 5), label=label)
        ax.legend()
        plt.show()

    # close logfile
    logfile.close()

    # open result and update header
    result_filename = '{}/xxx.new'.format(workdir)
    with fits.open(result_filename) as hdul:
        newheader = hdul[0].header
    newheader.add_comment('Astrometric solution computed')
    # save result
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), newheader)
    hdu.writeto(output_filename, overwrite=True)
    if verbose:
        print('-> file {} created'.format(output_filename))

    if interactive:
        input("Press <RETURN> to continue...")