.. _another_example_with_LSS_data:

******************************
Another example with LSSS data
******************************

.. note::

   This is a summary of the steps followed to carry out a quick reduction of
   the LSSS data.

The data must be located within a subdirectory corresponding to a particular
observing night:

::

  $ mkdir data_LSSS_test/
  $ cd data_LSSS_test
  $ mkdir 141214_LSSS
  $ cd 141214_LSSS

We place here, under ``141214_LSSS``, all the FITS files corresponding to this
test.  Since the images have the extension ``.fts``, it is necessary to replace
that extension by ``.fits``. The corresponding command (under the BASH shell)
is:

::

  $ for f in *.fts; do mv $f ${f%.*}.fits; done

It is also necessary to generate a rotated version of the two calibrations:

::

  $ filabres-rotate_flipstat masterbias2x2.fits

The previous command generates a file ``masterbias2x2r.fits``. 

Similarly:

::

  $ filabres-rotate_flipstat masterflat2x2.fits

generates a file ``masterflat2x2r.fits``.

Let's have a look to the keyword ``FLIPSTAT`` in these 4 calibration images:

::
  
  $ fitsheader master* -k flipstat -f
        filename        FLIPSTAT 
  ------------------- -----------
   masterbias2x2.fits            
  masterbias2x2r.fits Flip/Mirror
   masterflat2x2.fits            
  masterflat2x2r.fits Flip/Mirror

Move up in the directory tree and generate the setup files for filabres:

::

  $ cd ../..
  $ filabres --setup lsss data_LSSS_test

Check that there are no duplicated files (this step is actually not necessary
since there is only one subdirectory; with more than one observing night it is
useful to perfomr this check):

::

  $ filabres --check
  Night 171214_LSSS -> number of files:   336, ignored:     0 --> TOTAL:   336
  There are no duplicate files
  * program STOP

Classify the images (ignore the warning messages):

::

  $ filabres -rs initialize -v
  * instrument: lsss
  * datadir: data_LSSS_test/
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171214_LSSS']
  
  File ignored_images.yaml found
  Nights with images to be ignored: set()
  
  File image_header_corrections.yaml found
  Nights with image corrections: set()
  
  File forced_classifications.yaml found
  Nights with images with forced classification: set()
  
  Subdirectory ./lists/ not found. Creating it!
  Subdirectory ./lists/171214_LSSS not found. Creating it!
   
  * Working with night 171214_LSSS (1/1) ---> 338 FITS files
  -> Creating ./lists/171214_LSSS/imagedb_lsss.log
  WARNING: keyword MJD-OBS is missing in file 00308-S001-R001-C001-NoFilt.fits (set to 58101.026933680754)
  File 00308-S001-R001-C001-NoFilt.fits (1/338) classified as <science-imaging>
  ...
  ...
  WARNING: keyword RA is missing in file masterbias2x2.fits (set to None)
  WARNING: keyword DEC is missing in file masterbias2x2.fits (set to None)
  WARNING: keyword CLRBAND is missing in file masterbias2x2.fits (set to None)
  ...
  ...
  num_bias: 2
  num_wrong-bias: 0
  num_flat-imaging: 2
  num_wrong-flat-imaging: 0
  num_science-imaging: 334
  num_wrong-science-imaging: 0
  num_ignored: 0
  num_unclassified: 0
  num_wrong-instrument: 0
  -> Creating ./lists/171214_LSSS/imagedb_lsss.json
  * program STOP

Reduce the calibration frames (they are already reduced, but it is importat to
execute this step in order to insert the reduced calibrations in the
corresponding databases):

::

  $ filabres -rs bias -v
  * instrument: lsss
  * datadir: data_LSSS_test/
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171214_LSSS']
  
  Results database set to filabres_db_lsss_bias.json
  
  Subdirectory bias not found. Creating it!
  maxtimespan_hours: 0
  
  * Working with night 171214_LSSS (1/1)
  Reading file ./lists/171214_LSSS/imagedb_lsss.json
  Number of bias images found 2
  Subdirectory bias/171214_LSSS not found. Creating it!
  Number of different signatures found: 2
  
  Signature (1/2):
   - INSTRUME: SBIG ST-10 3 CCD Camera
   - NAXIS1: 1092
   - NAXIS2: 736
   - XORGSUBF: 0
   - YORGSUBF: 0
   - XBINNING: 2
   - YBINNING: 2
   - FLIPSTAT:
  Total number of images with this signature: 1
  ---
  -> Reduction starts at.: 2020-03-30 11:19:14.630663
  Working with signature SBIG ST-10 3 CCD Camera__1092__736__0__0__2__2__
  -> Number of images with expected signature and within time span: 1
   - data_LSSS_test/171214_LSSS/masterbias2x2.fits
  -> Output fname will be: bias/171214_LSSS/bias_masterbias2x2_red.fits
  WARNING: missing RA set to None
  WARNING: missing DEC set to None
  WARNING: missing MJD-OBS set to 57480.18763310183
  WARNING: missing CLRBAND set to None
  Creating bias/171214_LSSS/bias_masterbias2x2_red.fits
  Creating bias/171214_LSSS/bias_masterbias2x2_red.log
  -> Reduction ends at...: 2020-03-30 11:19:14.726327
  -> Time span...........: 0:00:00.095664
  
  Signature (2/2):
   - INSTRUME: SBIG ST-10 3 CCD Camera
   - NAXIS1: 1092
   - NAXIS2: 736
   - XORGSUBF: 0
   - YORGSUBF: 0
   - XBINNING: 2
   - YBINNING: 2
   - FLIPSTAT: Flip/Mirror
  Total number of images with this signature: 1
  ---
  -> Reduction starts at.: 2020-03-30 11:19:14.726645
  Working with signature SBIG ST-10 3 CCD Camera__1092__736__0__0__2__2__Flip/Mirror
  -> Number of images with expected signature and within time span: 1
   - data_LSSS_test/171214_LSSS/masterbias2x2r.fits
  -> Output fname will be: bias/171214_LSSS/bias_masterbias2x2r_red.fits
  WARNING: missing RA set to None
  WARNING: missing DEC set to None
  WARNING: missing MJD-OBS set to 57480.18763310183
  WARNING: missing CLRBAND set to None
  Creating bias/171214_LSSS/bias_masterbias2x2r_red.fits
  Creating bias/171214_LSSS/bias_masterbias2x2r_red.log
  -> Reduction ends at...: 2020-03-30 11:19:14.807924
  -> Time span...........: 0:00:00.081279
  * program STOP

::

  $ filabres -rs flat-imaging -v
  * instrument: lsss
  * datadir: data_LSSS_test/
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171214_LSSS']
  
  Results database set to filabres_db_lsss_flat-imaging.json
  
  Subdirectory flat-imaging not found. Creating it!
  maxtimespan_hours: 0
  
  * Working with night 171214_LSSS (1/1)
  Reading file ./lists/171214_LSSS/imagedb_lsss.json
  Number of flat-imaging images found 2
  Subdirectory flat-imaging/171214_LSSS not found. Creating it!
  Number of different signatures found: 2
  
  Signature (1/2):
   - INSTRUME: SBIG ST-10 3 CCD Camera
   - NAXIS1: 1092
   - NAXIS2: 736
   - XORGSUBF: 0
   - YORGSUBF: 0
   - XBINNING: 2
   - YBINNING: 2
   - FLIPSTAT: 
   - CLRBAND: R
  Total number of images with this signature: 1
  ---
  -> Reduction starts at.: 2020-03-30 11:33:57.742376
  Working with signature SBIG ST-10 3 CCD Camera__1092__736__0__0__2__2____R
  -> Number of images with expected signature and within time span: 1
   - data_LSSS_test/171214_LSSS/masterflat2x2.fits
  -> Output fname will be: flat-imaging/171214_LSSS/flat-imaging_masterflat2x2_red.fits
  WARNING: missing MJD-OBS set to 57485.798970254604
  WARNING: skipping basic reduction when generating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2_red.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2_red.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2_mask.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2_red.log
  -> Reduction ends at...: 2020-03-30 11:33:58.914955
  -> Time span...........: 0:00:01.172579
  
  Signature (2/2):
   - INSTRUME: SBIG ST-10 3 CCD Camera
   - NAXIS1: 1092
   - NAXIS2: 736
   - XORGSUBF: 0
   - YORGSUBF: 0
   - XBINNING: 2
   - YBINNING: 2
   - FLIPSTAT: Flip/Mirror
   - CLRBAND: R
  Total number of images with this signature: 1
  ---
  -> Reduction starts at.: 2020-03-30 11:33:58.915359
  Working with signature SBIG ST-10 3 CCD Camera__1092__736__0__0__2__2__Flip/Mirror__R
  -> Number of images with expected signature and within time span: 1
   - data_LSSS_test/171214_LSSS/masterflat2x2r.fits
  -> Output fname will be: flat-imaging/171214_LSSS/flat-imaging_masterflat2x2r_red.fits
  WARNING: missing MJD-OBS set to 57485.798970254604
  WARNING: skipping basic reduction when generating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2r_red.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2r_red.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2r_mask.fits
  Creating flat-imaging/171214_LSSS/flat-imaging_masterflat2x2r_red.log
  -> Reduction ends at...: 2020-03-30 11:34:00.084727
  -> Time span...........: 0:00:01.169368
  * program STOP

The final step is the reduction of the scientific images (ignore the WARNINGS):

::

  $ filabres -rs science-imaging
  * Number of nights found: 1

  * Working with night 171214_LSSS (1/1)
  ---
  -> Working with file 00308-S001-R001-C001-NoFilt.fits (1/334)  [Night 1/1]
  -> Input file name is......: data_LSSS_test/171214_LSSS/00308-S001-R001-C001-NoFilt.fits
  -> Output file name will be: science-imaging/171214_LSSS/science-imaging_00308-S001-R001-C001-NoFilt_red.fits
  -> Reduction starts at.....: 2020-03-30 17:08:52.561091
  -> Reduction ends at.......: 2020-03-30 17:10:07.375212
  -> Elapsed time............: 0:01:14.814121
  $ mv science-imaging/171214_LSSS/reduction.log science-imaging/171214_LSSS/science-imaging_00308-S001-R001-C001-NoFilt_red/
  ---
  -> Working with file 00308-S001-R002-C001-NoFilt.fits (2/334)  [Night 1/1]
  -> Input file name is......: data_LSSS_test/171214_LSSS/00308-S001-R002-C001-NoFilt.fits
  -> Output file name will be: science-imaging/171214_LSSS/science-imaging_00308-S001-R002-C001-NoFilt_red.fits
  -> Reduction starts at.....: 2020-03-30 17:10:07.381744
  -> Reduction ends at.......: 2020-03-30 17:10:20.691468
  -> Elapsed time............: 0:00:13.309724
  $ mv science-imaging/171214_LSSS/reduction.log science-imaging/171214_LSSS/science-imaging_00308-S001-R002-C001-NoFilt_red/
  ...
  ...

Note that the redution of the first image takes longer because it is necessary
to retrieve the GAIA data for the astrometric calibration with Astrometry.net.
The remaining scientific images, which pointings are close enough to the one
corresponding to the first image, do not require that step (the same catalogue
of GAIA objects is reused).

You can easily check the quality of the astrometric solution:

::

  $ filabres -lr science-imaging -k astr1_ntargets -k astr2_ntargets \
  -k astr1_meanerr -k astr2_meanerr 
      ASTR1_NTARGETS ASTR2_NTARGETS  ASTR1_MEANERR  ASTR2_MEANERR                                                                              file
  1              132            367        0.67439        0.12894  science-imaging/171214_LSSS/science-imaging_00308-S001-R001-C001-NoFilt_red.fits
  2              132            379        0.67678        0.13156  science-imaging/171214_LSSS/science-imaging_00308-S001-R002-C001-NoFilt_red.fits
  3              132            362        0.66732        0.14693  science-imaging/171214_LSSS/science-imaging_00308-S001-R003-C001-NoFilt_red.fits
  ...
  ...

The prefixes ``ASTR1_`` and ``ASTR2_`` indicate values corresponding to the
astrometric calibration with the Astrometry.net and AstrOmatic.net tools,
respectively. ``NTARGETS`` and ``MEANERR`` refer to the number of objects
employed to compute the calibration and the mean error (in arcsec).

Solving some problems with the astrometric calibration
------------------------------------------------------

The image number 193 shows a large astrometric error. It is possible to repeat
the reduction of this image, forcing the downloading of GAIA data (centered
around the central coordinates of this particular image) without reusing the
GAIA data initially downloaded for the astrometric calibration of the first
image. This affects the initial astrometric calibration with Astrometry.net
tools, which subsequently also has an effect on the refined calibration with
AstrOmatic.net tools. For this purpose one has to use the argument
``-ng/--no_reuse_gaia``:

::

  $ filabres -rs science-imaging --filename 00308-S001-R193-C001-NoFilt.fits -v -i --force -ng
  ...
  ...
  Astrometric calibration of science-imaging/171214_LSSS/science-imaging_00308-S001-R193-C001-NoFilt_red.fits
  Creating configuration file science-imaging/171214_LSSS/work/myastrometry.cfg
  Central coordinates:
  <SkyCoord (FK5: equinox=2017-12-14T03:57:29.879): (ra, dec) in deg
      (132.2155, 12.23583333)>
  <SkyCoord (FK5: equinox=J2000.000): (ra, dec) in deg
      (131.9693779, 12.30282281)>
  -> Forcing downloading of GAIA catalogue close the field pointing
  Subdirectory science-imaging/171214_LSSS/index000002 not found. Creating it!
  -> Creating science-imaging/171214_LSSS/index000002/gaialog.log
  ...
  ...

Note that a new ``index000002`` subdirectory has been created, where the
additional GAIA data have been stored.
