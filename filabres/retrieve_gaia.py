# -*- coding: utf-8 -*-
#
# Copyright 2020 Universidad Complutense de Madrid
#
# This file is part of filabres
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from astroquery.gaia import Gaia

NMAXGAIA = 2000


def retrieve_gaia(gaiadr_source, ra_deg, dec_deg, radius_deg, magnitude, loggaia):
    """
    Retrieve GAIA data.

    Cone search around ra_deg, dec_deg, within a radius given by
    radius_deg, and within a given limiting magnitude.

    Parameters
    ==========
    gaiadr_source : str
        String identifying the Gaia DR version to be used.
        For example: 'gaiadr3.gaia_source'. This string is
        declared in the file setup_filabres.yaml.
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
    job_result : astropy table
        Result of the cone search
    """
    gaia_query_line1 = f'SELECT TOP {NMAXGAIA} SOURCE_ID, ref_epoch, ' \
                       'ra, ra_error, dec, dec_error, ' \
                       'parallax, parallax_error, ' \
                       'pmra, pmra_error, pmdec, pmdec_error, ' \
                       'phot_g_mean_mag, bp_rp, ' \
                       'radial_velocity, radial_velocity_error'
    gaia_query_line2 = f'FROM {gaiadr_source}'
    gaia_query_line3 = f'''WHERE CONTAINS(POINT('ICRS',{gaiadr_source}.ra,{gaiadr_source}.dec), ''' + \
                       '''CIRCLE('ICRS',''' + \
                       f'{ra_deg},{dec_deg},{radius_deg}' + \
                       '))=1'
    gaia_query_line4 = f'AND phot_g_mean_mag < {magnitude}'
    gaia_query_line = gaia_query_line1 + ' ' + gaia_query_line2 + ' ' + gaia_query_line3 + ' ' + gaia_query_line4

    loggaia.write('Querying GAIA data with phot_g_mean_mag={:.2f}\n'.format(magnitude))

    loggaia.write(gaia_query_line + '\n')
    # retrieve GAIA data (see example in https://www.cosmos.esa.int/web/gaia-users/archive/use-cases#ClusterAnalysisPythonTutorial)
    try:
        job = Gaia.launch_job_async(gaia_query_line)
        job_result = job.get_results()
    except:
        job_result = None
    return gaia_query_line, job_result
