.. _reduction_of_flat-imaging:

*************************
Reduction of flat-imaging
*************************

.. note::

   **Filabres** computes master calibration images for each night. Within 
   each night, individual calibration exposures within a given time span (given
   by the keyword ``maxtimespan_hours`` in the file
   ``configuration_cafos.yaml``) are combined.  Note that in order to be
   included in a particular master calibration, the corresponding individual
   images should also have the same signature, i.e., the same values for the
   set of FITS keywords listed under ``signature`` in the file
   ``configuration_cafos.yaml`` for the considered image type (``bias``,
   ``flat-imaging``,...).

The reduction of flat-imaging files is quite similar to the process followed
for the bias images. Note that now the signature of the images also depends on
the position of the grism wheel (keyword ``INSGRID``; no grism for imaging
mode), the filter employed during the observation (keyword ``INSFLID``), and
the absence of the wollaston prism required for imaging polarimetry (keywords
``INSPOFPI`` and ``INSPOROT``).

::

  $ filabres -rs flat-imaging
  * Number of nights found: 58

  * Working with night 170225_t2_CAFOS (1/58)
  ---
  Working with signature SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1__GRISM-11__FILT- 9__FREE__0
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:20:04-cal-krek_red.fits
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:20:04-cal-krek_mask.fits
  ---
  Working with signature SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1__GRISM-11__FILT- 9__FREE__0
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170226-06:24:27-cal-krek_red.fits
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170226-06:24:27-cal-krek_mask.fits
  ---
  Working with signature SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1__GRISM-11__FILT-10__FREE__0
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:49:51-cal-krek_red.fits
  Creating flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:49:51-cal-krek_mask.fits
  ...
  ...
  * Working with night 171228_t2_CAFOS (57/58)
  ---
  Working with signature SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1__GRISM-11__FILT- 5__FREE__0
  Creating flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  Creating flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_mask.fits
  
  * Working with night 171230_t2_CAFOS (58/58)
  ---
  Working with signature SITE#1d_15__800__800__[601,601:1400,1400]__1__1__GRISM-11__FILT-11__FREE__0
  Creating flat-imaging/171230_t2_CAFOS/flat-imaging_caf-20171229-10:04:54-cal-lilj_red.fits
  Creating flat-imaging/171230_t2_CAFOS/flat-imaging_caf-20171229-10:04:54-cal-lilj_mask.fits
  ---
  Working with signature SITE#1d_15__800__800__[601,601:1400,1400]__1__1__GRISM-11__FILT-11__FREE__0
  Creating flat-imaging/171230_t2_CAFOS/flat-imaging_caf-20171231-06:30:10-cal-lilj_red.fits
  Creating flat-imaging/171230_t2_CAFOS/flat-imaging_caf-20171231-06:30:10-cal-lilj_mask.fits
  * program STOP
  


Several warning messages may appear during the reduction of these images
(ignore them).

Note that within each night one (or several) master flat-imaging frames (and
their associated mask images) are created.  The information on the terminal
indicates the corresponding signature.

The master flat-imaging frames are stored in the subdirectory ``flat-imaging``
under the current directory:

::

  $ tree flat-imaging
  flat-imaging/
  ├── 170225_t2_CAFOS
  │   ├── flat-imaging_caf-20170224-20:20:04-cal-krek_mask.fits
  │   ├── flat-imaging_caf-20170224-20:20:04-cal-krek_red.fits
  │   ├── flat-imaging_caf-20170224-20:49:51-cal-krek_mask.fits
  │   ├── flat-imaging_caf-20170224-20:49:51-cal-krek_red.fits
  │   ├── flat-imaging_caf-20170224-21:12:37-cal-krek_mask.fits
  │   ├── flat-imaging_caf-20170224-21:12:37-cal-krek_red.fits
  │   ├── flat-imaging_caf-20170225-18:28:50-cal-krek_mask.fits
  │   ├── flat-imaging_caf-20170225-18:28:50-cal-krek_red.fits
  │   ├── flat-imaging_caf-20170226-06:05:08-cal-krek_mask.fits
  │   ├── flat-imaging_caf-20170226-06:05:08-cal-krek_red.fits
  │   ├── flat-imaging_caf-20170226-06:24:27-cal-krek_mask.fits
  │   └── flat-imaging_caf-20170226-06:24:27-cal-krek_red.fits
  ├── 170403_t2_CAFOS
  │   ├── flat-imaging_caf-20170403-17:19:21-cal-lilj_mask.fits
  │   ├── flat-imaging_caf-20170403-17:19:21-cal-lilj_red.fits
  │   ├── flat-imaging_caf-20170403-18:44:42-cal-lilj_mask.fits
  │   └── flat-imaging_caf-20170403-18:44:42-cal-lilj_red.fits
  ...
  ...
  ├── 171228_t2_CAFOS
  │   ├── flat-imaging_caf-20171228-13:14:11-cal-bard_mask.fits
  │   └── flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  └── 171230_t2_CAFOS
      ├── flat-imaging_caf-20171229-10:04:54-cal-lilj_mask.fits
      ├── flat-imaging_caf-20171229-10:04:54-cal-lilj_red.fits
      ├── flat-imaging_caf-20171231-06:30:10-cal-lilj_mask.fits
      └── flat-imaging_caf-20171231-06:30:10-cal-lilj_red.fits

If you want to get more information concerning the reduction of these type of
images, just add -v to increase the verbosity level. For example, we can try to
repeat the reduction of the night ``171228_t2_CAFOS``:

::

  $ filabres -rs flat-imaging -n 171228* -v
  * instrument: cafos
  * datadir: /Volumes/NicoPassport/CAHA/CAFOS2017
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171228_t2_CAFOS']

  Results database set to filabres_db_cafos_flat-imaging.json
  
  Subdirectory flat-imaging found
  maxtimespan_hours: 1
  
  * Working with night 171228_t2_CAFOS (1/1)
  Reading file ./lists/171228_t2_CAFOS/imagedb_cafos.json
  Number of flat-imaging images found 10
  Subdirectory flat-imaging/171228_t2_CAFOS found
  Number of different signatures found: 1
  Signature (1/1):
   - CCDNAME: SITE#1d_15
   - NAXIS1: 1700
   - NAXIS2: 1700
   - DATASEC: [201,201:1900,1900]
   - CCDBINX: 1
   - CCDBINY: 1
   - INSGRID: GRISM-11
   - INSFLID: FILT- 5
   - INSPOFPI: FREE
   - INSPOROT: 0
  Total number of images with this signature: 10
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:14:11-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:15:44-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:17:17-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:18:51-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:20:24-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:21:57-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:23:31-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:25:05-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:26:39-cal-bard.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171228_t2_CAFOS/caf-20171228-13:28:12-cal-bard.fits
  -> Number of images with expected signature and within time span: 10
  File flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits already exists: skipping reduction.
  * program STOP
   
For this particular night, all the flat-imaging files exhibit a single
signature. The 10 available individual frames were obtained within one hour.
For that reason all of them are selected to be combined in a single master
flat-imaging frame. The name of the output file is taken from the first image
in the sequence of 10 images, adding the prefix ``flat-imaging_`` and the
suffix ``_red`` (the latter prior to the extension ``.fits``). 

An additional output file, containing a mask of useful pixels, is also
generated, using the same file name but changing the suffix ``_red`` by
``_mask``. In this mask a value of 0 is assigned to pixels without useful
signal (probably due to vignetting), whereas a value of 1 is employed for the
pixels in the useful image region.

Note however that since **filabres** has detected that the output image already
exists, the output file is not overwritten. You can force to overwrite the
output file by using the additional argument ``--force`` in the command line:

::

  $ filabres -rs flat-imaging -n 171228* -v --force
  ...
  ...
  -> Number of images with expected signature and within time span: 10
  -> output fname will be flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  -> output mname will be flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_mask.fits
  Deleting flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  Deleting flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_mask.fits
  WARNING: deleting previous database entry: flat-imaging --> SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1__GRISM-11__FILT- 5__FREE__0 --> 58115.55635
  
  Calibration database set to filabres_db_cafos_bias.json
  -> looking for calibration bias with signature SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1
  ->   mjdobsarray.......: [57905.6372  58102.60078 58105.56892 58108.57108 58111.0489  58112.72261
   58112.82979 58115.568  ]
  ->   looking for mjdobs: 58115.5515
  ->   nearest value is..: 58115.56800
  ->   delta_mjd (days)..: 0.016499999997904524
  Median value in frame #1/10: 28403.5
  Median value in frame #2/10: 28546.0
  Median value in frame #3/10: 28278.5
  Median value in frame #4/10: 28265.0
  Median value in frame #5/10: 28226.0
  Median value in frame #6/10: 28062.5
  Median value in frame #7/10: 28058.0
  Median value in frame #8/10: 28298.5
  Median value in frame #9/10: 28038.5
  Median value in frame #10/10: 28083.0
  Working with signature SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1__GRISM-11__FILT- 5__FREE__0
  Creating flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  Creating flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_mask.fits
  * program STOP

Note that the reduction of the flat-imaging files requires the use of a master
bias with a particular signature, in this case
``SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1``, which is compatible with
the signature of the considered flat-imaging files:
``SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1__GRISM-11__FILT-
5__FREE__0`` (the bias signature does not depend on the use of grism and/or
filters). Several master bias frames with this signature are found, each one
with a different modified Julian Date. The selected one is the closest, in
time, with the observing time of the flat images. In addition,  the median
signal in each individual exposure is also shown (note that this value is
computed in the useful image region, where the computed mask is different from
zero).
   
.. _database_of_master_flat-imaging_frames:

Database of master flat-imaging frames
======================================

The reduction of the flat-imaging files generates a file, placed in the current
directory, called ``filabres_db_cafos_flat-imaging.json``. This constitutes a
database with the information of all the flat-imaging images, sorted by
signature and, within each signature, sorted by the Modified Julian Date (FITS
keyword MJD-OBS). In this way, when a master flat-imaging is needed in the
reduction of a scientific image, filabres can determine the required
calibration signature and then select the closest calibration to the
corresponding observation time.

The structure of ``filabres_db_cafos_flat-imaging.json`` is similar to the one
previously explained for ``filabres_db_cafos_bias.json`` in the section
:ref:`database_of_master_bias_frames`, and is not going to be repeated here.

.. _checking_the_flat-imaging_reduction:

Checking the flat-imaging reduction
===================================

In order to obtain a list with al the reduced flat-imaging frames just execute:

::

  $ filabres -lr flat-imaging
                                                                                   file
  1   flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:20:04-cal-krek_red.fits
  2   flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170226-06:24:27-cal-krek_red.fits
  3   flat-imaging/170225_t2_CAFOS/flat-imaging_caf-20170224-20:49:51-cal-krek_red.fits
  ...
  ...
  84  flat-imaging/171225_t2_CAFOS/flat-imaging_caf-20171225-17:31:09-cal-bard_red.fits
  85  flat-imaging/171225_t2_CAFOS/flat-imaging_caf-20171225-20:09:53-cal-bard_red.fits
  86  flat-imaging/171228_t2_CAFOS/flat-imaging_caf-20171228-13:14:11-cal-bard_red.fits
  Total: 86 files

The available keywords for this type of images are:

::

  (filabfes) $ filabres -lr flat-imaging -k all
  Valid keywords: ['NAXIS', 'NAXIS1', 'NAXIS2', 'OBJECT', 'RA', 'DEC',
  'EQUINOX', 'DATE', 'MJD-OBS', 'AIRMASS', 'EXPTIME', 'INSTRUME', 'CCDNAME',
  'ORIGSECX', 'ORIGSECY', 'CCDSEC', 'BIASSEC', 'DATASEC', 'CCDBINX',
  'CCDBINY', 'IMAGETYP', 'INSTRMOD', 'INSAPID', 'INSTRSCL', 'INSTRPIX',
  'INSTRPX0', 'INSTRPY0', 'INSFLID', 'INSFLNAM', 'INSGRID', 'INSGRNAM',
  'INSGRROT', 'INSGRWL0', 'INSGRRES', 'INSPOFPI', 'INSPOROT', 'INSFPZ',
  'INSFPWL', 'INSFPDWL', 'INSFPORD', 'INSCALST', 'INSCALID', 'INSCALNM',
  'NPOINTS', 'FMINIMUM', 'QUANT025', 'QUANT159', 'QUANT250', 'QUANT500',
  'QUANT750', 'QUANT841', 'QUANT975', 'FMAXIMUM', 'ROBUSTSTD', 'NORIGIN',
  'IERR_BIAS', 'DELTA_MJD_BIAS', 'BIAS_FNAME', 'IERR_FLAT']

Note some new useful keywords:

- ``IERR_BIAS``: flag that indicates whether there was a problem when trying to
  retrieve the master bias frame corresponding to the signature of the flat
  images. The value 0 means that the master bias was found, whereas a value of
  1 indicates that no master bias was found with the requested signature (in
  this case, the median value of the closest bias is chosen, independently of
  its signature).

- ``DELTA_MJD_BIAS``: time distance (days) between the master bias and the flat
  images being reduced.

- ``BIAS_FNAME``: path to the master bias image employed in the reduction of
  the flat images.

- ``IERR_FLAT``: flag that indicates a problem in the reduction of the flat
  images themselves (a negative median signal for example). These images should
  be revised.

For example, it is possible to quickly determine if ``IERR_BIAS`` or
``IERR_FLAT`` are different from zero in any of the reduced flat-imaging
frames:

::

  $ filabres -lr flat-imaging --filter 'k[ierr_bias] != 0'
  Total: 0 files

::

  $ filabres -lr flat-imaging  --filter 'k[ierr_flat] != 0'
  Total: 0 files

None of the reduced flat-imaging frames has had any problem in the reduction
process.



It is also useful to examine some statistical parameters of the reduced images:

::

  $ filabres -lr flat-imaging -k quant250 -k quant500 -k quant750 -k robuststd -pxy
  ...
  ...

.. image:: images/pxy_reduced_flat-imaging.png
   :width: 100%
   :alt: Reduced flat-imaging summary

We find that all the reduced flat-imaging frames exhibit the expected
statistical behavior

.. _removing_invalid_reduced_flat-imaging:

Removing invalid reduced flat-imaging
=====================================

In this case there is no apparent reason to remove any of the reduced
flat-imaging frames. If that were the case, the method would be similar to that
described in section :ref:`removing_invalid_reduced_bias` for the reduced
master bias images.

