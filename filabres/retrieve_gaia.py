import pyvo

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
