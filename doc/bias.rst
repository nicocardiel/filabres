.. _reduction_of_bias_images:

************************
Reduction of bias images
************************

.. warning::

   The following documentation has been prepared executing the commands in a
   terminal running the bash shell. If you are using the Z shell (that at the
   time of writing is the default in mac OS) it is important to remember that
   the wildcards employed in some `filabres` parameters need to be provided
   enclosed in double quotes.

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


The first calibration images to be reduced are the bias frames. The reduction
is performed by using the reduction step ``bias``:

::

  $ filabres -rs bias
  * Number of nights found: 58
  ---
  Working with signature SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1
  Creating bias/170225_t2_CAFOS/bias_caf-20170224-21:27:48-cal-krek_red.fits
  ---
  Working with signature SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
  Creating bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits
  
  * Working with night 170226_t2_CAFOS (2/58)
  ---
  Working with signature SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
  Creating bias/170226_t2_CAFOS/bias_caf-20170226-11:39:37-cal-bomd_red.fits

  ...
  ...

  * Working with night 171230_t2_CAFOS (58/58)
  ---
  Working with signature SITE#1d_15__800__800__[601,601:1400,1400]__1__1
  Creating bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits
  * program STOP

Several warning messages may appear during the reduction of these images (they
should be the same found when classifying the images; just
ignore them). 

Note that within each night one (or several) master bias images are created.
The information on the terminal indicates the corresponding signature.

The master bias frames are stored in the subdirectory ``bias`` under the 
current directory:

::

  $ tree bias
  bias
  ├── 170225_t2_CAFOS
  │   ├── bias_caf-20170224-21:27:48-cal-krek_red.fits
  │   ├── bias_caf-20170224-21:27:48-cal-krek_red.log
  │   ├── bias_caf-20170225-10:03:09-cal-bomd_red.fits
  │   └── bias_caf-20170225-10:03:09-cal-bomd_red.log
  ├── 170226_t2_CAFOS
  │   ├── bias_caf-20170226-11:39:37-cal-bomd_red.fits
  │   └── bias_caf-20170226-11:39:37-cal-bomd_red.log
  ...
  ...
  ├── 171228_t2_CAFOS
  │   ├── bias_caf-20171228-13:31:20-cal-bard_red.fits
  │   ├── bias_caf-20171228-13:31:20-cal-bard_red.log
  │   ├── bias_caf-20171228-13:50:00-cal-agui_red.fits
  │   └── bias_caf-20171228-13:50:00-cal-agui_red.log
  └── 171230_t2_CAFOS
      ├── bias_caf-20171229-10:12:35-cal-lilj_red.fits
      └── bias_caf-20171229-10:12:35-cal-lilj_red.log

If you want to get more information concerning the reduction of these type of
images, just add ``-v`` to increase the verbosity level. For example, we
can try to repeat the reduction of the last night ``171230_t2_CAFOS``:


::

  $ filabres -rs bias -n 171230* -v
  * instrument: cafos
  * datadir: /Volumes/NicoPassport/CAHA/CAFOS2017
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171230_t2_CAFOS']
  
  Results database set to filabres_db_cafos_bias.json
  
  Subdirectory bias found
  maxtimespan_hours: 1
  
  * Working with night 171230_t2_CAFOS (1/1)
  Reading file ./lists/171230_t2_CAFOS/imagedb_cafos.json
  Number of bias images found 10
  Subdirectory bias/171230_t2_CAFOS found
  Number of different signatures found: 1
  Signature (1/1):
   - CCDNAME: SITE#1d_15
   - NAXIS1: 800
   - NAXIS2: 800
   - DATASEC: [601,601:1400,1400]
   - CCDBINX: 1
   - CCDBINY: 1
  Total number of images with this signature: 10
  -> Number of images with expected signature and within time span: 10
  File bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits already exists: skipping reduction.
  * program STOP

In the last execution, **filabres** has detected that the output image already
exists. For that reason the reduction of the corresponding files has been
halted in order to avoid overwritting the output file. You can force the
repetition of the reduction by using the additional argument ``--force`` in the
command line:

::

  $ filabres -rs bias -n 171230* -v --force
  * instrument: cafos
  * datadir: /Volumes/NicoPassport/CAHA/CAFOS2017
  * ignored_images_file: ignored_images.yaml
  * image_header_corrections_file: image_header_corrections.yaml
  * forced_classifications_file: forced_classifications.yaml
  * Loading instrument configuration
  * Number of nights found: 1
  * List of nights: ['171230_t2_CAFOS']
  
  Results database set to filabres_db_cafos_bias.json
  
  Subdirectory bias found
  maxtimespan_hours: 1
  
  * Working with night 171230_t2_CAFOS (1/1)
  Reading file ./lists/171230_t2_CAFOS/imagedb_cafos.json
  Number of bias images found 10
  Subdirectory bias/171230_t2_CAFOS found
  Number of different signatures found: 1
  
  Signature (1/1):
   - CCDNAME: SITE#1d_15
   - NAXIS1: 800
   - NAXIS2: 800
   - DATASEC: [601,601:1400,1400]
   - CCDBINX: 1
   - CCDBINY: 1
  Total number of images with this signature: 10
  ---
  -> Reduction starts at.: 2020-03-26 16:38:09.283082
  Working with signature SITE#1d_15__800__800__[601,601:1400,1400]__1__1
  -> Number of images with expected signature and within time span: 10
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:12:35-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:13:11-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:13:48-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:14:23-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:14:59-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:15:35-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:11-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:48-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:17:24-cal-lilj.fits
   - /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:18:00-cal-lilj.fits
  -> Output fname will be: bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits
  Deleting bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits
  WARNING: deleting previous database entry: bias --> SITE#1d_15__800__800__[601,601:1400,1400]__1__1 --> 58116.42725
  Creating bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits
  Creating bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.log
  -> Reduction ends at...: 2020-03-26 16:38:09.525570
  -> Time span...........: 0:00:00.242488
  * program STOP
  
For this particular night, the bias images exhibit a single signature. The 10
available individual frames where obtained within one hour (the
``maxtimespan_hours`` value). For that reason all of them are selected to be
combined in a single master bias frame. The name of the output file is taken
from the first image in the sequence of 10 images, adding the prefix ``bias_``
and the suffix ``_red`` (the latter prior to the extension ``.fits``). In
addition, a log file with the same name as the output file, but with the
extension ``.log``, is also generated.


.. _database_of_master_bias_frames:

Database of master bias frames
==============================

The reduction of the bias images generates a file, placed in the current
directory, called ``filabres_db_cafos_bias.json``. This constitutes a database
with the information of all the master bias images, sorted by signature and,
within each signature, sorted by the Modified Julian Date (FITS keyword
``MJD-OBS``). In this way, when a master bias is needed in the reduction of
flatfield or a scientific image, **filabres** can determine the required
calibration signature and then select the closest calibration to the
corresponding observation time.

.. warning::

   Feel free to skip the rest of this subsection. This information is not
   essential for the regular use of **filabres**.

The structure of ``filabres_db_cafos_bias.json`` is the following:

::

   {
     "bias": {...}
     "signaturekeys": [...]
   }

Under ``signaturekeys`` one finds the list of FITS keywords that determine
the signature of each master bias frame:

::

   "signaturekeys":
       "CCDNAME",
       "NAXIS1",
       "NAXIS2",
       "DATASEC",
       "CCDBINX",
       "CCDBINY"

The ``bias`` key contains a nested dictionary:

::

   "bias":
      "SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1": {...}
      "SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1": {...}
      "SITE#1d_15__1024__1024__[513,513:1536,1536]__1__1": {...}
      "SITE#1d_15__800__800__[625,625:1424,1424]__1__1": {...}
      "SITE#1d_15__512__850__[256,100:768,950]__2__2": {...}
      "SITE#1d_15__1400__2048__[301,1:1700,2048]__1__1": {...}
      "SITE#1d_15__850__512__[100,256:950,768]__2__2": {...}
      "SITE#1d_15__1700__1700__[201,201:1900,1900]__1__1": {...}
      "SITE#1d_15__850__850__[100,100:950,950]__2__2": {...}
      "SITE#1d_15__800__800__[601,601:1400,1400]__1__1": {...}
      "SITE#1d_15__400__2048__[801,1:1200,2048]__1__1": {...}
      "SITE#1d_15__801__1027__[624,561:1424,1587]__1__1": {...}
      "SITE#1d_15__501__501__[250,250:750,750]__2__2": {...}

Each displayed key is the signature string built from the concatenation of the
involved FITS keyword values. Within each signature one finds another nested
dictionary where the keys are the Modified Julian Date:

::

    "SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1":
      "57809.42257": {...}
      "57810.48956": {...}
      "57890.69435": {...}
      "57891.57056": {...}
      "57897.69934": {...}
      "57898.17553": {...}
      "57898.69377": {...}
      "57899.16265": {...}
      "57899.65963": {...}
      "57900.17332": {...}
      "57900.69400": {...}
      "57901.68921": {...}
      "57905.54971": {...}

Within each date, the contents have the following structure:

::

      "57809.42257": {
        "night": "170225_t2_CAFOS",
        "signature": {
          "CCDNAME": "SITE#1d_15",
          "NAXIS1": 1000,
          "NAXIS2": 2048,
          "DATASEC": "[501,1:1500,2048]",
          "CCDBINX": 1,
          "CCDBINY": 1
        },
        "fname": "bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits",
        "statsumm": {
          "NPOINTS": 2048000,
          "FMINIMUM": 0.5,
          "QUANT025": 657.0,
          "QUANT159": 661.5,
          "QUANT250": 663.5,
          "QUANT500": 665.5,
          "QUANT750": 668.0,
          "QUANT841": 669.5,
          "QUANT975": 673.0,
          "FMAXIMUM": 13798.0,
          "ROBUSTSTD": 3.3358499999999998
        },
        "masterkeywords": {
          "NAXIS": 2,
          "NAXIS1": 1000,
          "NAXIS2": 2048,
          "OBJECT": "[bias]",
          "RA": 303.714233,
          "DEC": 37.23009,
          "EQUINOX": 2000.0,
          "DATE": "2017-02-25T10:03:09",
          "MJD-OBS": 57809.4188,
          "AIRMASS": 1.0,
          "EXPTIME": 0.0,
          "INSTRUME": "CAFOS 2.2",
          "CCDNAME": "SITE#1d_15",
          "ORIGSECX": 2048.0,
          "ORIGSECY": 2048.0,
          "CCDSEC": "[501,1:1500,2048]",
          "BIASSEC": "[0,1:0,2048]",
          "DATASEC": "[501,1:1500,2048]",
          "CCDBINX": 1,
          "CCDBINY": 1,
          "IMAGETYP": "bias",
          "INSTRMOD": "Polarizer",
          "INSAPID": "SLIT",
          "INSTRSCL": 0.53,
          "INSTRPIX": 24.0,
          "INSTRPX0": 1054.57,
          "INSTRPY0": 1060.85,
          "INSFLID": "FILT-12",
          "INSFLNAM": "free",
          "INSGRID": "GRISM- 1",
          "INSGRNAM": "blue-100",
          "INSGRROT": 359.72,
          "INSGRWL0": 423.8,
          "INSGRRES": 0.199,
          "INSPOFPI": "FREE",
          "INSPOROT": 0,
          "INSFPZ": 0,
          "INSFPWL": "not used",
          "INSFPDWL": "not used",
          "INSFPORD": "not used",
          "INSCALST": false,
          "INSCALID": "Lamp",
          "INSCALNM": "    /    /"
        },
        "norigin": 10,
        "originf": [
          "caf-20170225-10:03:09-cal-bomd.fits",
          "caf-20170225-10:04:20-cal-bomd.fits",
          "caf-20170225-10:05:32-cal-bomd.fits",
          "caf-20170225-10:06:44-cal-bomd.fits",
          "caf-20170225-10:07:56-cal-bomd.fits",
          "caf-20170225-10:09:08-cal-bomd.fits",
          "caf-20170225-10:10:19-cal-bomd.fits",
          "caf-20170225-10:11:31-cal-bomd.fits",
          "caf-20170225-10:12:43-cal-bomd.fits",
          "caf-20170225-10:13:55-cal-bomd.fits"
        ]
      }

Without entering into too many details, the displayed information includes
the file name for the corresponding master bias ``fname``, the individual
images involved ``originf``, the values of all the FITS keywords listed in
``masterkeywords``, and the statistical summary of the master image
``statsumm``, to mention the most relevant items.

.. _checking_the_bias_reduction:

Checking the bias reduction
===========================

Fortunately, you do not need to manually examine the file
``filabres_db_cafos_bias.json`` to check the reduction of bias images.

The argument ``-lr/--list_reduced`` allows to list the result of the reduction
of some particular images. It works in a similar way as the
``-lc/--list_classified`` argument, previously used to list the classified
images (*be careful not to confuse them*).

If you simply execute:

::

  $ filabres -lr
  Valid imagetypes:
  - bias (available=True)
  - flat-imaging (available=False)
  - flat-imaging-wollaston (available=False)
  - flat-spectroscopy (available=False)
  - arc (available=False)
  - science-imaging (available=False)
  - science-imaging-wollaston (available=False)
  - science-spectroscopy (available=False)

you get a list of possible image types. Note that here only ``bias`` is
available (is the only reduction step we have performed so far).

In order to check the reduction of the bias images just execute:

::

  $ filabres -lr bias
  filabres -lr bias
                                                                   file
  1   bias/170225_t2_CAFOS/bias_caf-20170224-21:27:48-cal-krek_red.fits
  2   bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits
  3   bias/170226_t2_CAFOS/bias_caf-20170226-11:39:37-cal-bomd_red.fits
  ...
  ...
  82  bias/170807_t2_CAFOS/bias_caf-20170808-04:55:29-cal-schn_red.fits
  83  bias/170928_t2_CAFOS/bias_caf-20170928-15:14:46-cal-wenj_red.fits
  84  bias/170929_t2_CAFOS/bias_caf-20170929-14:26:11-cal-wenj_red.fits
  Total: 84 files

It is possible to filter the list by night (wildcards allowed here). For
example, for the first night:

::

  $ filabres -lr bias -n 170225*
                                                                  file
  1  bias/170225_t2_CAFOS/bias_caf-20170224-21:27:48-cal-krek_red.fits
  2  bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits
  Total: 2 files

There are two master bias for this night, with different signature. It is 
possible to display them (``-pi``):

::

   $ filabres -lr bias -n 170225* -pi
   ...
   ...

.. image:: images/pi_reduced_bias1_20170224.png
   :width: 100%
   :alt: Reduced bias image 1, night 20170224

.. image:: images/pi_reduced_bias2_20170224.png
   :width: 100%
   :alt: Reduced bias image 2, 20170224


You can use ``-k all`` to show the whole list of available keywords:

::

   $ filabres -lr bias -k all
   Valid keywords: ['NAXIS', 'NAXIS1', 'NAXIS2', 'OBJECT', 'RA', 'DEC',
   'EQUINOX', 'DATE', 'MJD-OBS', 'AIRMASS', 'EXPTIME', 'INSTRUME', 'CCDNAME',
   'ORIGSECX', 'ORIGSECY', 'CCDSEC', 'BIASSEC', 'DATASEC', 'CCDBINX',
   'CCDBINY', 'IMAGETYP', 'INSTRMOD', 'INSAPID', 'INSTRSCL', 'INSTRPIX',
   'INSTRPX0', 'INSTRPY0', 'INSFLID', 'INSFLNAM', 'INSGRID', 'INSGRNAM',
   'INSGRROT', 'INSGRWL0', 'INSGRRES', 'INSPOFPI', 'INSPOROT', 'INSFPZ',
   'INSFPWL', 'INSFPDWL', 'INSFPORD', 'INSCALST', 'INSCALID', 'INSCALNM',
   'NPOINTS', 'FMINIMUM', 'QUANT025', 'QUANT159', 'QUANT250', 'QUANT500',
   'QUANT750', 'QUANT841', 'QUANT975', 'FMAXIMUM', 'ROBUSTSTD', 'NORIGIN']


Remember that you can generate a table with any selection of these keywords
(``-k <keyword1> -k <keyword2>...``), sort that table by any combination of
keywords (``-ks <keyword1> -ks <keyword2>...``), and generate XY plot with
combinations of numerical keywords (``-pxy``).

For the bias images, it is interesting to check the plot that compares the
evolution of the median bias level (``QUANT500``) with the observation date
(``MJD-OBS``), sorting the table by robust standard deviation (``ROBUSTSTD``):

::

  $ filabres -lr bias -k mjd-obs -k quant500 -ks robuststd -pxy
          MJD-OBS   QUANT500  ROBUSTSTD                                                               file
  79  58073.58750  657.00000  1.48260    bias/171116_t2_CAFOS/bias_caf-20171116-14:06:06-cal-lilj_red.fits
  59  58078.64000  666.00000  1.85325    bias/171121_t2_CAFOS/bias_caf-20171121-15:21:37-cal-bomd_red.fits
  46  58057.59300  665.00000  2.22390    bias/171101_t2_CAFOS/bias_caf-20171031-14:14:01-cal-agui_red.fits
  ...
  ...
  57  57933.73719  666.00000  8.89560    bias/170629_t2_CAFOS/bias_caf-20170629-17:41:33-cal-mirl_red.fits
  53  57876.04090  698.00000  14.08470   bias/170502_t2_CAFOS/bias_caf-20170503-00:58:59-sci-alex_red.fits
  14  57905.54600  723.00000  24.09225   bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits
  Total: 84 files

.. image:: images/pxy_reduced_bias.png
   :width: 100%
   :alt: Variation of the reduced bias level and the robust standard devitation

Since we have sorted this last table by ``ROBUSTSTD``, the last row, which
corresponds to
``bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits``,
indicates that this image has an unusually high median and robust standard
deviation. That image corresponding to night ``20170601``. Let's display the
master bias generated in that night:

::

  $ filabres -lr bias -k mjd-obs -k quant500 -ks robuststd -n 170601* -pi
        MJD-OBS  QUANT500  ROBUSTSTD                                                               file
  2  57905.6352  680.0     5.18910    bias/170601_t2_CAFOS/bias_caf-20170601-15:14:47-cal-pelm_red.fits
  1  57905.5460  723.0     24.09225   bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits
  Total: 2 files

The first master bias looks normal:

.. image:: images/pi_reduced_bias1_20170601.png
   :width: 100%
   :alt: Reduced bias 1 from 20170601

However, the second bias exhibit a clear illumination gradient, specially
noticeable in the upper left corner of the detector:

.. image:: images/pi_reduced_bias2_20170601.png
   :width: 100%
   :alt: Reduced bias 2 from 20170601

It is likely that the individual bias exposures employed to generate the last
master bias frame have the same problem. You can verify this by using
``-of/--originf <path_reduced_calibration_image>``, that list the individual images employed in the generation
of a particular reduced calibration image (this new arguments allows the
additional use of ``-k <keyword>``, ``-ks <keyword>``, ``-pxy`` and ``-pi``):

::

  $ filabres -of bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits \
  -k quant500 -k robuststd
  Signature: SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
  Available images with this signature:
  MJD-OBS: 57809.42257, calibration: bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits
  MJD-OBS: 57810.48956, calibration: bias/170226_t2_CAFOS/bias_caf-20170226-11:39:37-cal-bomd_red.fits
  MJD-OBS: 57890.69435, calibration: bias/170517_t2_CAFOS/bias_caf-20170517-16:34:30-cal-bomd_red.fits
  MJD-OBS: 57891.57056, calibration: bias/170518_t2_CAFOS/bias_caf-20170518-13:36:14-cal-bomd_red.fits
  MJD-OBS: 57897.69934, calibration: bias/170524_t2_CAFOS/bias_caf-20170524-16:41:41-cal-boeh_red.fits
  MJD-OBS: 57898.17553, calibration: bias/170524_t2_CAFOS/bias_caf-20170525-04:07:28-cal-boeh_red.fits
  MJD-OBS: 57898.69377, calibration: bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits
  MJD-OBS: 57899.16265, calibration: bias/170525_t2_CAFOS/bias_caf-20170526-03:48:53-cal-boeh_red.fits
  MJD-OBS: 57899.65963, calibration: bias/170526_t2_CAFOS/bias_caf-20170526-15:44:34-cal-boeh_red.fits
  MJD-OBS: 57900.17332, calibration: bias/170526_t2_CAFOS/bias_caf-20170527-04:04:16-cal-boeh_red.fits
  MJD-OBS: 57900.69400, calibration: bias/170527_t2_CAFOS/bias_caf-20170527-16:34:04-cal-boeh_red.fits
  MJD-OBS: 57901.68921, calibration: bias/170528_t2_CAFOS/bias_caf-20170528-16:27:05-cal-boeh_red.fits
  MJD-OBS: 57905.54971, calibration: bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits (*)
  ---
  List of individual frames:
    (involved in the computation of bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits)
      QUANT500  ROBUSTSTD                                                                                      file
  1   722.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:06:15-cal-bomd.fits
  2   722.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:07:26-cal-bomd.fits
  3   722.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:08:38-cal-bomd.fits
  4   722.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:09:50-cal-bomd.fits
  5   722.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:11:02-cal-bomd.fits
  6   723.0     25.9455    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:12:14-cal-bomd.fits
  7   723.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:13:25-cal-bomd.fits
  8   723.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:14:37-cal-bomd.fits
  9   723.0     25.2042    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:15:48-cal-bomd.fits
  10  723.0     25.9455    /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:17:01-cal-bomd.fits
  Total: 10 files

The output of the last command provides very useful information:

- ``Signature``: indicates the particular signature of the calibration image.

- ``Available reduced images with this signature``: the modified Julian Date
  and the name of the calibration file is given. An asterisk ``(*)`` appears
  after the name of the reduced image we are investigating. **The list reveals
  that there are other reduced bias images with the same signature**. This is
  important because if we decide to remove the suspicious calibration image,
  there will be additional calibration images with the same signature that can
  be employed (although from different nights).

- ``List of individual frames:`` list of individual images employed in the
  reduction of the reduced image indicated after the argument ``-of``. This
  list is a table with the additional requested keywords.

In this case, we confirm that the high median and robust standard deviation
values are also present in the individual images employed to generate the
suspicious reduced bias image. Not only that. The illumination gradient is also
present in the 10 individual images, as can be easily visualized using ``-pi``:

::

  $ filabres -of bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits \
  -k quant500 -k robuststd -pi
  ...
  ...

(Note: the 10 displayed images are quite similar to the one shown here)

.. image:: images/pi_individual_wrongbias_20170601.png
   :width: 100%
   :alt: Individual wrong bias night 20170601

The problem that we have detected with those bias images may be present in
other images as well. In order to dig a bit more in this issue, it is useful to
inspect other reduced bias frames with high ``ROBUSTSTD``.

::

  (filabres ) $ filabres -lr bias -k quant500 -ks robuststd
  ...
  ...

Let's have a look to images with ``ROBUSTSTD`` > 5:

::

  $ filabres -lr bias -k quant500 -ks robuststd --filter 'k[robuststd] > 5' -pi
  ...
  ...

Apart from
``bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits``, there is
another reduced bias with the same problem:
``bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits``:

.. image:: images/pi_reduced_bias1_20170525.png
   :width: 100%
   :alt: Reduced bias 1 from 20170525

Again, we examine the individual exposures associated to this last reduced
image:

::

  $ filabres -of bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits \
  -k quant500 -k robuststd -pi
  Signature: SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
  Available images with this signature:
  MJD-OBS: 57809.42257, calibration: bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits
  MJD-OBS: 57810.48956, calibration: bias/170226_t2_CAFOS/bias_caf-20170226-11:39:37-cal-bomd_red.fits
  MJD-OBS: 57890.69435, calibration: bias/170517_t2_CAFOS/bias_caf-20170517-16:34:30-cal-bomd_red.fits
  MJD-OBS: 57891.57056, calibration: bias/170518_t2_CAFOS/bias_caf-20170518-13:36:14-cal-bomd_red.fits
  MJD-OBS: 57897.69934, calibration: bias/170524_t2_CAFOS/bias_caf-20170524-16:41:41-cal-boeh_red.fits
  MJD-OBS: 57898.17553, calibration: bias/170524_t2_CAFOS/bias_caf-20170525-04:07:28-cal-boeh_red.fits
  MJD-OBS: 57898.69377, calibration: bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits (*)
  MJD-OBS: 57899.16265, calibration: bias/170525_t2_CAFOS/bias_caf-20170526-03:48:53-cal-boeh_red.fits
  MJD-OBS: 57899.65963, calibration: bias/170526_t2_CAFOS/bias_caf-20170526-15:44:34-cal-boeh_red.fits
  MJD-OBS: 57900.17332, calibration: bias/170526_t2_CAFOS/bias_caf-20170527-04:04:16-cal-boeh_red.fits
  MJD-OBS: 57900.69400, calibration: bias/170527_t2_CAFOS/bias_caf-20170527-16:34:04-cal-boeh_red.fits
  MJD-OBS: 57901.68921, calibration: bias/170528_t2_CAFOS/bias_caf-20170528-16:27:05-cal-boeh_red.fits
  MJD-OBS: 57905.54971, calibration: bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits
  ---
  List of individual frames:
    (involved in the computation of bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits)
      QUANT500  ROBUSTSTD                                                                                      file
  1   683.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:33:40-cal-boeh.fits
  2   683.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:34:51-cal-boeh.fits
  3   683.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:36:02-cal-boeh.fits
  4   683.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:37:14-cal-boeh.fits
  5   682.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:38:26-cal-boeh.fits
  6   682.0     11.8608    /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:39:37-cal-boeh.fits
  7   678.0     8.1543     /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:40:49-cal-boeh.fits
  8   678.0     8.1543     /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:42:01-cal-boeh.fits
  9   678.0     8.1543     /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:43:13-cal-boeh.fits
  10  678.0     8.1543     /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:44:25-cal-boeh.fits
  Total: 10 files
  
Again, the problem is present in the individual images. 

.. _removing_invalid_reduced_bias:

Removing invalid reduced bias
=============================

.. warning::

   In order to remove a particular reduced calibration (in this case a master
   bias) it is important to follow **all the steps** here given.

1. Include the individual images involved in the generation of the reduced
   image in ``ignored_images.yaml``: in this example, we
   want to exclude 10 images from night ``170525_t2_CAFOS`` and another set of
   10 images from ``170601_t2_CAFOS``. The easiest way
   is to repeat the execution of the last **filabres** command, by adding
   ``-lm basic`` (basic list mode), which will provide a list of ten files
   that we can *cut and paste* in the file ``ignored_images.yaml``. Step by
   step, the procedure is:

   - 1.a. For the first wrong reduced bias execute:

     ::

       $ filabres -of bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits -lm basic
       ...
       ...
       List of individual frames:
       (involved in the computation of bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits)
        - caf-20170525-16:33:40-cal-boeh.fits
        - caf-20170525-16:34:51-cal-boeh.fits
        - caf-20170525-16:36:02-cal-boeh.fits
        - caf-20170525-16:37:14-cal-boeh.fits
        - caf-20170525-16:38:26-cal-boeh.fits
        - caf-20170525-16:39:37-cal-boeh.fits
        - caf-20170525-16:40:49-cal-boeh.fits
        - caf-20170525-16:42:01-cal-boeh.fits
        - caf-20170525-16:43:13-cal-boeh.fits
        - caf-20170525-16:44:25-cal-boeh.fits
       Total: 10 files

     For the second wrong reduced bias:

     ::


       $ filabres -of bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits -lm basic
       ...
       ...
       List of individual frames:
       (involved in the computation of bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits)
        - caf-20170601-13:06:15-cal-bomd.fits
        - caf-20170601-13:07:26-cal-bomd.fits
        - caf-20170601-13:08:38-cal-bomd.fits
        - caf-20170601-13:09:50-cal-bomd.fits
        - caf-20170601-13:11:02-cal-bomd.fits
        - caf-20170601-13:12:14-cal-bomd.fits
        - caf-20170601-13:13:25-cal-bomd.fits
        - caf-20170601-13:14:37-cal-bomd.fits
        - caf-20170601-13:15:48-cal-bomd.fits
        - caf-20170601-13:17:01-cal-bomd.fits
       Total: 10 files

   - 1.b. Cut and paste each block of 10 lines starting by ``-`` into the file
     ``ignored_image.yaml``, creating a new block for each night.  Considering
     that we already had 4 blocks in this file, we insert two new blocks blocks
     (the order of the blocks is irrelevant, but here we preserve the order
     given by the observing night just to facilitate the organization of the
     blocks), so the final content of this file is:

     .. literalinclude:: ignored_images_v2.yaml
        :linenos:
        :lineno-start: 1
        :emphasize-lines: 17-43

     Note that the new blocks correspond to the highlighted lines 17 to 43. In
     this case, the explicit names of the files have been used (no
     wildcards employed).

2. Re-run the image classification for the corresponding observing nights: this
   will regenerate the local image database ``imagedb_cafos.json`` for
   ``170525_t2_CAFOS`` and ``170601_t2_CAFOS``, ignoring the problematic files.
   Note that if you simple execute:

   ::

     $ filabres -rs initialize -n 170525*
     * Number of nights found: 1
     File ./lists/170525_t2_CAFOS/imagedb_cafos.json already exists: skipping directory.
     * program STOP

   nothing really happens because the local database already exists. You have
   to force the classification in order to override the database file (using
   the argument ``--force``):

   ::

     $ filabres -rs initialize -n 170525* --force
     * Number of nights found: 1
     * Working with night 170601_t2_CAFOS (1/1) ---> 62 FITS files
     * program STOP

   Check that the images have in fact been ignored:

   ::

     $ filabres -lc ignored -n 170525*
                                                                                             file
     1   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:33:40-cal-boeh.fits
     2   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:34:51-cal-boeh.fits
     3   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:36:02-cal-boeh.fits
     4   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:37:14-cal-boeh.fits
     5   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:38:26-cal-boeh.fits
     6   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:39:37-cal-boeh.fits
     7   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:40:49-cal-boeh.fits
     8   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:42:01-cal-boeh.fits
     9   /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:43:13-cal-boeh.fits
     10  /Volumes/NicoPassport/CAHA/CAFOS2017/170525_t2_CAFOS/caf-20170525-16:44:25-cal-boeh.fits
     Total: 10 files

   Repeat the same for the second night:

   ::

     $ filabres -rs initialize -n 170601* --force
     * Number of nights found: 1
     * Working with night 170601_t2_CAFOS (1/1) ---> 96 FITS files
     * program STOP

   ::

     $ filabres -lc ignored -n 170601*
                                                                                             file
     1   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:06:15-cal-bomd.fits
     2   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:07:26-cal-bomd.fits
     3   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:08:38-cal-bomd.fits
     4   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:09:50-cal-bomd.fits
     5   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:11:02-cal-bomd.fits
     6   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:12:14-cal-bomd.fits
     7   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:13:25-cal-bomd.fits
     8   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:14:37-cal-bomd.fits
     9   /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:15:48-cal-bomd.fits
     10  /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:17:01-cal-bomd.fits
     Total: 10 files


3. Remove the problematic reduced images from ``filabres_db_cafos_bias.json``,
   the database that contains all the reduced bias frames. Note that the
   undesired reduced calibration is not only still present in that database,
   but the reduced FITS files are still under the ``bias`` subdirectory that
   hosts all the reduced bias frames (so far we have only removed the
   individual original FITS files from the classication of the images). 

   Taking care of removing both the reduced images from the database and the
   actual FITS files from the hard disk is handled by **filabres** using a
   single command. For the first wrong reduced bias:

   ::

     $ filabres --delete bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits 
     Image to be deleted bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits
     Signature: SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
     MJD-OBS..: 57898.69377
     Number of reduced bias images with this signature: 13
     -> Updating filabres_db_cafos_bias.json
     -> Deleting file bias/170525_t2_CAFOS/bias_caf-20170525-16:33:40-cal-boeh_red.fits
     * program STOP

   For the second wrong reduced bias:

   ::

     $ filabres --delete bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits
     Image to be deleted bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits
     Signature: SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
     MJD-OBS..: 57905.54971
     Number of reduced bias images with this signature: 12
     -> Updating filabres_db_cafos_bias.json
     -> Deleting file bias/170601_t2_CAFOS/bias_caf-20170601-13:06:15-cal-bomd_red.fits

