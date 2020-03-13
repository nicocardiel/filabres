.. _reduction_of_calibration_images:

*******************************
Reduction of calibration images
*******************************

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


Bias
====

Reduction of bias images
------------------------

The first calibration images to be reduced are the bias frames:

::

   (filabres) $ filabres -rs bias
   * Number of nights found: 58
   
   * Working with night 170225_t2_CAFOS (1/58)
   Creating bias/170225_t2_CAFOS/bias_caf-20170224-21:27:48-cal-krek_red.fits with signature SITE#1d_15__1650__1650__[251,221:1900,1870]__1__1
   Creating bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits with signature SITE#1d_15__1000__2048__[501,1:1500,2048]__1__1
   
   ...
   ...

   * Working with night 171230_t2_CAFOS (58/58)
   Creating bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits with signature SITE#1d_15__800__800__[601,601:1400,1400]__1__1
   * program STOP

Several warning messages may appear during the reduction of these images (they
should be the same found when classifying the images; just
ignore them). 

Note that within each night one (or several) master bias images are created.
The information on the terminal indicates the corresponding signature.

The master bias frames are stored in the subdirectory ``bias`` under the 
current directory:

::

   (filabres) $ tree bias
   bias
   ├── 170225_t2_CAFOS
   │   ├── bias_caf-20170224-21:27:48-cal-krek_red.fits
   │   └── bias_caf-20170225-10:03:09-cal-bomd_red.fits
   ├── 170226_t2_CAFOS
   │   └── bias_caf-20170226-11:39:37-cal-bomd_red.fits
   ├── 170319_t2_CAFOS
   │   └── bias_caf-20170319-09:20:09-cal-agui_red.fits
   ├── 170331_t2_CAFOS
   │   └── bias_caf-20170331-16:47:53-cal-agui_red.fits
   ├── 170403_t2_CAFOS
   │   └── bias_caf-20170403-17:27:07-cal-lilj_red.fits
   ...
   ...
   ├── 171225_t2_CAFOS
   │   ├── bias_caf-20171225-17:14:00-cal-bard_red.fits
   │   ├── bias_caf-20171225-17:43:07-cal-bard_red.fits
   │   └── bias_caf-20171225-19:48:21-cal-bard_red.fits
   ├── 171228_t2_CAFOS
   │   ├── bias_caf-20171228-13:31:20-cal-bard_red.fits
   │   └── bias_caf-20171228-13:50:00-cal-agui_red.fits
   └── 171230_t2_CAFOS
       └── bias_caf-20171229-10:12:35-cal-lilj_red.fits

If you want to get more information concerning the reduction of these type of
images, just add ``-v`` to increase the verbosity level. For example, we
can try to repeat the reduction of the last night ``171230_t2_CAFOS``:


::

   (filabres) $ filabres -rs bias -n 171230* -v --force
   * instrument............: cafos
   * datadir...............: /Users/cardiel/CAFOS2017
   * ignored_images_file...: ignored_images.yaml
   * image_corrections_file: image_header_corrections.yaml
   * Loading instrument configuration
   * Number of nights found: 1
   * List of nights: ['171230_t2_CAFOS']
   
   Results database set to filabres_db_cafos_bias.json
   
   Subdirectory bias found
   
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
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:12:35-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:13:11-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:13:48-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:14:23-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:14:59-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:15:35-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:11-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:48-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:17:24-cal-lilj.fits
    - /Users/cardiel/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:18:00-cal-lilj.fits
   -> Number of images with expected signature and within time span: 10
   File bias/171230_t2_CAFOS/bias_caf-20171229-10:12:35-cal-lilj_red.fits already exists: skipping reduction.
   * program STOP

For this particular night, the bias images exhibit a single signature. The 10
available individual frames where obtained within one hour. For that reason all
of them are selected to be combined in a single master bias frame. The name of
output file is taken from the first image in the sequence of 10 images, adding
the prefix ``bias_`` and the suffix ``_red`` (the latter prior to the extension
``.fits``). Note however that, since **filabres** detects that the output image
already exists, the output file is not overwritten (you can force to overwrite
the output file by using the additional argument ``--force`` in the command
line).

Database of bias master frames
------------------------------

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

Without entering in too many details, the displayed information includes
the file name for the corresponding master bias ``fname``, the individual
images involved ``originf``, the values of all the FITS keywords listed in
``masterkeywords``, and the statistical summary of the master image
``statsumm``, to mention the most relevant items.

Checking the bias reduction
---------------------------

Fortunately, you do not need to manually examine the file
``filabres_db_cafos_bias.json`` to check the reduction of bias images.

The argument ``-lr`` allows to list the result of the reduction of some
particular images. It works in a similar way as the ``-lc`` argument,
previously used to list the classified images (*be careful not to confuse
them*).

In order to check the reduction of the bias images just execute:

::

   (filabres) $ filabres -lr bias
                                                                    file NAXIS1 NAXIS2
   1   bias/170225_t2_CAFOS/bias_caf-20170224-21:27:48-cal-krek_red.fits  1650   1650 
   2   bias/170225_t2_CAFOS/bias_caf-20170225-10:03:09-cal-bomd_red.fits  1000   2048 
   3   bias/170226_t2_CAFOS/bias_caf-20170226-11:39:37-cal-bomd_red.fits  1000   2048 
   ...
   ...
   81  bias/170807_t2_CAFOS/bias_caf-20170808-04:55:29-cal-schn_red.fits  400    2048 
   82  bias/170928_t2_CAFOS/bias_caf-20170928-15:14:46-cal-wenj_red.fits  801    1027 
   83  bias/170929_t2_CAFOS/bias_caf-20170929-14:26:11-cal-wenj_red.fits  501    501  
   Total: 83 files

Flat-imaging
============

Reduction of flat-imaging images
--------------------------------

Database of flat-imaging master frames
--------------------------------------

Checking the flat-imaging reduction
-----------------------------------

