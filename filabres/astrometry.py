from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, FK5
from astropy.io import fits
from astropy.time import Time
import json
import numpy as np
import os
import pyvo
import subprocess


def astrometry(image2d, header, nightdir, interactive, indexid,
               verbose, debug=False):
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
    nightdir : str
        Directory where the raw image is stored and the auxiliary
        images created by astrometry will be placed.
    interactive : bool
        If True, enable interactive execution (e.g. plots,...).
    indexid : int
        Running number to identify the index file created with the
        GAIA objects.
    verbose : bool
        If True, display intermediate information.
    debug : bool
        Display additional debugging information.
    """

    if verbose:
        print('\nPerforming astrometric calibration')

    # read JSON file with central coordinates of fields already calibrated
    jsonfilename = '{}/central_pointings.json'.format(nightdir)
    if os.path.exists(jsonfilename):
        with open(jsonfilename) as jfile:
            ccbase = json.load(jfile)
    else:
        ccbase = dict()

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
    if verbose:
        print('Central coordinates:')
        print(c_fk5_dateobs)
        print(c_fk5_j2000)

    # ToDo: define properly the search_radius_degree
    # ToDo: refine limiting magnitude when looking for GAIA data
    # generate query for GAIA
    search_radius_degree = 10/60
    gaia_query_line1 = 'SELECT TOP 2000 source_id, ref_epoch, ' \
                       'ra, ra_error, dec, dec_error, ' \
                       'parallax, parallax_error, ' \
                       'pmra, pmra_error, pmdec, pmdec_error, ' \
                       'phot_g_mean_mag, bp_rp, ' \
                       'radial_velocity, radial_velocity_error, ' \
                       'a_g_val'
    gaia_query_line2 = 'FROM gdr2.gaia_source'
    gaia_query_line3 = '''WHERE CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec), ''' + \
                       '''CIRCLE('ICRS',''' + \
                       '{},{},{}'.format(c_fk5_j2000.ra.degree, c_fk5_j2000.dec.degree, search_radius_degree) + '))=1'
    gaia_query_line4 = 'AND phot_g_mean_mag < 16'

    gaia_query = gaia_query_line1 + ' ' + gaia_query_line2 + ' ' + gaia_query_line3 + ' ' + gaia_query_line4

    if verbose:
        print(gaia_query)

    # retrieve GAIA data using the Table Access Protocol;
    # see specific details for retrieval of GAIA data in
    # https://gaia.aip.de/cms/documentation/tap-interface/
    tap_service = pyvo.dal.TAPService('https://gaia.aip.de/tap')
    tap_result = tap_service.run_sync(gaia_query)
    if verbose:
        print(tap_result.to_table())

    # proper motion correction
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

    # create index subdir
    subdir = 'index{:06d}'.format(indexid)
    newsubdir = nightdir + '/' + subdir
    if os.path.isdir(newsubdir):
        if verbose:
            print('Subdirectory {} found'.format(newsubdir))
    else:
        if verbose:
            print('Subdirectory {} not found. Creating it!'.format(newsubdir))
        os.makedirs(newsubdir)

    # save GAIA objects in FITS binary table
    hdr = fits.Header()
    hdr.add_history('GAIA objets selected with following query:')
    hdr.add_history(gaia_query_line1)
    hdr.add_history(gaia_query_line2)
    hdr.add_history(gaia_query_line3)
    hdr.add_history(gaia_query_line4)
    hdr.add_history('---')
    hdr.add_history('Note that RA and DEC have been corrected from proper motion')
    primary_hdu = fits.PrimaryHDU(header=hdr)
    col1 = fits.Column(name='source_id', format='K', array=source_id)
    col2 = fits.Column(name='ra', format='D', array=ra_corrected)
    col3 = fits.Column(name='dec', format='D', array=dec_corrected)
    col4 = fits.Column(name='phot_g_mean_mag', format='E', array=phot_g_mean_mag)
    hdu = fits.BinTableHDU.from_columns([col1, col2, col3, col4])
    hdul = fits.HDUList([primary_hdu, hdu])
    hdul.writeto(nightdir + '/' + subdir + '/GaiaDR2-query.fits', overwrite=True)

    # ToDo: refine -P value when executing build-astrometry-index
    # generate index file with GAIA data
    command = 'build-astrometry-index -i {}/{}/GaiaDR2-query.fits'.format(nightdir, subdir)
    command += ' -o {}/{}/index-image.fits'.format(nightdir, subdir)
    command += ' -A ra -D dec -S phot_g_mean_mag'
    command += ' -P 2 -E -I {}'.format(indexid)
    if verbose:
        print(command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    if verbose:
        print(p.stdout.read().decode('utf-8'))
    p.stdout.close()

    # update JSON file with central coordinates of fields already calibrated
    ccbase[subdir] = {'ra': c_fk5_j2000.ra.degree, 'dec': c_fk5_j2000.dec.degree}
    with open(jsonfilename, 'w') as outfile:
        json.dump(ccbase, outfile, indent=2)

    command = 'cp {}/{}/index-image.fits {}/work/'.format(nightdir, subdir, nightdir)
    if verbose:
        print(command)
        input('paused here!')
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    if verbose:
        print(p.stdout.read().decode('utf-8'))
    p.stdout.close()

    # save temporary FITS file
    output_filename = '{}/xxx.fits'.format(workdir)
    hdu = fits.PrimaryHDU(image2d.astype(np.float32), header)
    hdu.writeto(output_filename, overwrite=True)

    # solve field
    command = 'cd {}; '.format(workdir)
    command += 'solve-field -p -l 300'
    command += ' --config myastrometry.cfg --overwrite'.format(newsubdir)
    command += ' --ra ' + str(c_fk5_j2000.ra.degree)
    command += ' --dec ' + str(c_fk5_j2000.dec.degree)
    command += ' --radius 1 xxx.fits'.format(nightdir)
    if verbose:
        print(command)
    input("Press <RETURN> to continue...")
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True)
    if verbose:
        print(p.stdout.read().decode('utf-8'))
    p.stdout.close()

    # load wcs from file
    w = WCS('{}/xxx.wcs'.format(workdir))
    print(w.printwcs())

    header.add_history('Computing astrometric solution:')
    header.update(w.to_header(relax=True))
