.. _image_classification:

********************
Image classification
********************

Rules for the classification of the images
==========================================

The image
classification will take place by generating a local database (a JSON file
called ``imagedb_cafos.json``) for each observing night. For this purpose,
**filabres** will follow the rules provided in the instrument configuration
file ``configuration_cafos.yaml``. Note that this file is embedded in the
distribution source code, under the directory ``filabres/instrument/``.

.. warning::

   Since the modification of the file ``configuration_cafos.yaml`` could change
   the classification of the images perfomerd by **filabres**, in principle
   this file should not be modified by a normal user. In any case, if you want
   to change it, it will be necessary to reinstall the code for the changes to
   be applied.

In its first hierarchical level, this file ``configuration_cafos.yaml`` defines
the following keys: ``instname``, ``version``, ``requirements``,
``masterkeywords``, and ``imagetypes``:

::

   instname: cafos
   version: 2.3
   requirements:
     INSTRUME: 'CAFOS 2.2'
   masterkeywords:
     - NAXIS      # number of data axes
     - NAXIS1     # length of data axis 1
     - NAXIS2     # length of data axis 2
     - OBJECT     # Target description
     ...
     ...
   imagetypes:
     bias:
       ...
       ...
     flat-imaging:
       ...
       ...
     flat-spectroscopy:
       ...
       ...
     arc:
       ...
       ...
     science-imaging:
       ...
       ...
     science-spectroscopy:
       ...
       ...

- ``instname``: the instrument name.

- ``version``: the version of the instrument configuration file.

- ``requirements``: the value of predefined FITS keywords that must be
  satisfied in order to classified the initial image within one of the
  categories defined below. If these requirements are not fulfilled, the image
  will be classified as ``wrong-instrument``. For this particular example, a
  single requirement has been defined: the keyword ``INSTRUME`` must be defined
  in the FITS header and must be set to ``CAFOS 2.2``.

- ``masterkeywords``: list of keywords that must be stored in the local
  database.

- ``imagetypes``: the different categories into which the initial images will
  be classified are provided as second-level dictionary of image types (e.g.:
  ``bias``, ``flat-imaging``, ``science-imaging``, etc.). 
  In order to proceed with this classification, each image type
  should be defined according to a third-level dictionary of
  keywords. For example, the image type ``bias`` is defined as:

  ::

     imagetype:
       bias:
         executable: True
         classification: calibration
         requirements:
           IMAGETYP: 'bias'
         requirementx:
           EXPTIME: 0.0
           QUANT975.LT.: 1000
         signature:
           - CCDNAME
           - NAXIS1
           - NAXIS2
           - DATASEC
           - CCDBINX
           - CCDBINY
         maxtimespan_hours: 1

  The relevant keywords in this third-level dictionary are:

  - ``executable``: if True, the reduction of this image type has been
    considered in **filabres**. Otherwise, the implementation of the reduction
    of this type of images is still pending.

  - ``classification``: so far only two possibilities are valid here:
    ``calibration`` or ``science``. Note that calibration images will be
    combined to generate master calibrations (e.g., bias frames
    obtained in a predefined time span will be coadded), whereas science frames
    will be independently reduced (i.e., without image coaddition).

  - ``requirements``: conditions on FITS keywords that must be met in order to
    classify a particular image within the considered category. All these
    requirements are mandatory. Otherwise the image will be classified as
    ``unclassified``. 

  - ``requirementx``: additional set of requirements . If any of these new
    requirements is not met, the image will be classified as
    ``wrong-<imagetype>`` (e.g., ``bias-wrong``, ``flat-imaging-wrong``, etc.). 
    Note that the separation of the requirements in
    these two sets (``requirements`` and ``requirementx``) allows to generate a
    classification where images initially classified within a given image type
    (because they verify all the ``requirements``) can be flagged as suspicious 
    because they exhibit an unexpected property (defined in the
    ``requirementx``), such as anomalous exposure time or signal.

Note that images previously included in the file ``ignored_images.yaml`` will
be classified as ``ignored``.

Inital image classification
===========================

The image classification is performed by using:

::

   (filabres) $ filabres -rs initialize
   * Number of nights found: 58
   * Working with night 170225_t2_CAFOS (1/58) ---> 140 FITS files
   * Working with night 170226_t2_CAFOS (2/58) ---> 55 FITS files
   ...
   ...

A few warnings may be raised during the execution of the program. In particular
for the CAFOS 2017 data, the ``MJD-OBS`` is negative in some images and
**filabres** recomputes it. In other cases, ``HIERARCHCAHA DET CCDS`` is found,
when it sould be ``HIERARCH CAHA DET CCDS``. You can be safely ignored these
warning messages.

After the execution of previous command, a new subdirectory ``lists`` should
have appear in your working directory, containing subdirectories for all the
observing nights:

::

   (filabres) $ ls lists/
   170225_t2_CAFOS/ 170506_t2_CAFOS/ 170601_t2_CAFOS/ 170807_t2_CAFOS/
   170226_t2_CAFOS/ 170507_t2_CAFOS/ 170602_t2_CAFOS/ 170809_t2_CAFOS/
   170319_t2_CAFOS/ 170517_t2_CAFOS/ 170621_t2_CAFOS/ 170811_t2_CAFOS/
   170331_t2_CAFOS/ 170518_t2_CAFOS/ 170627_t2_CAFOS/ 170825_t2_CAFOS/
   170403_t2_CAFOS/ 170519_t2_CAFOS/ 170628_t2_CAFOS/ 170903_t2_CAFOS/
   170408_t2_CAFOS/ 170524_t2_CAFOS/ 170629_t2_CAFOS/ 170918_t2_CAFOS/
   170420_t2_CAFOS/ 170525_t2_CAFOS/ 170713_t2_CAFOS/ 170926_t2_CAFOS/
   170422_t2_CAFOS/ 170526_t2_CAFOS/ 170720_t2_CAFOS/ 170928_t2_CAFOS/
   170502_t2_CAFOS/ 170527_t2_CAFOS/ 170724_t2_CAFOS/
   170505_t2_CAFOS/ 170528_t2_CAFOS/ 170731_t2_CAFOS/

Within each night, a file ``imagedb_cafos.json`` should have been created, 
storing the image classification.

::

   (filabres) $ ls lists/170225_t2_CAFOS/
   imagedb_cafos.json

For those nights with images that have raised WARNINGS during the image
classfication, an additional ``imagedb_cafos.log`` file should also have been
created containing the warning messages.


Examine the image classification
================================

Select image type
-----------------

Although you can always try to open any of the files ``imagedb_cafos.json``
directly (using a proper JSON editor), **filabres** provides an easier way to
examine the image classification previously performed (using the argument
``-lc <imagetype>``; list classified images). 
For example, to list the different image types available:

::

   (filabres) $ filabres -lc
   Valid imagetypes:
   - bias
   - flat-imaging
   - flat-spectroscopy
   - arc
   - science-imaging
   - science-spectroscopy
   - wrong-bias
   - wrong-flat-imaging
   - wrong-flat-spectroscopy
   - wrong-arc
   - wrong-science-imaging
   - wrong-science-spectroscopy
   - wrong-instrument
   - ignored
   - unclassified

You can repeat the same command by adding any of the above image types:

::

   (filabres) $ filabres -lc bias
                                                                                            file NAXIS1 NAXIS2
   1    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:27:48-cal-krek.fits  1650   1650 
   2    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:29:09-cal-krek.fits  1650   1650 
   3    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:30:31-cal-krek.fits  1650   1650 
   4    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:31:52-cal-krek.fits  1650   1650 
   ...
   ...
   824  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:48-cal-lilj.fits  800    800  
   825  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:17:24-cal-lilj.fits  800    800  
   826  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:18:00-cal-lilj.fits  800    800  
   Total: 826 files

By default the list displays the full path to the original files and their
dimensiones (``NAXIS1`` and ``NAXIS2``).
   
Select image type and observing nights
--------------------------------------

It is possible to constraint the list of files to those corresponding to a
given subset of nights (using the argument ``-n <night>``; wildcards are valid
here):

::

   (filabres) $ filabres -lc bias -n 1702*
                                                                                              file NAXIS1 NAXIS2
   1   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:27:48-cal-krek.fits  1650   1650 
   2   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:29:09-cal-krek.fits  1650   1650 
   3   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:30:31-cal-krek.fits  1650   1650 
   ...
   ...
   28  /Volumes/NicoPassport/CAHA/CAFOS2017/170226_t2_CAFOS/caf-20170226-11:47:59-cal-bomd.fits  1000   2048 
   29  /Volumes/NicoPassport/CAHA/CAFOS2017/170226_t2_CAFOS/caf-20170226-11:49:11-cal-bomd.fits  1000   2048 
   30  /Volumes/NicoPassport/CAHA/CAFOS2017/170226_t2_CAFOS/caf-20170226-11:50:23-cal-bomd.fits  1000   2048 
   Total: 30 files

Select image type and relevant keywords
---------------------------------------

You can also display the values of relevant keywords belonging to the
``masterkeywords`` list in the file ``configuration_cafos.yaml``. If you don't
remember them, don't worry: use first ``-k all`` to display all the available
keywords:

::

   (filabres) $ filabres -lc bias -k all
   Valid keywords: ['NAXIS', 'NAXIS1', 'NAXIS2', 'OBJECT', 'RA', 'DEC',
   'EQUINOX', 'DATE', 'MJD-OBS', 'AIRMASS', 'EXPTIME', 'INSTRUME', 'CCDNAME',
   'ORIGSECX', 'ORIGSECY', 'CCDSEC', 'BIASSEC', 'DATASEC', 'CCDBINX',
   'CCDBINY', 'IMAGETYP', 'INSTRMOD', 'INSAPID', 'INSTRSCL', 'INSTRPIX',
   'INSTRPX0', 'INSTRPY0', 'INSFLID', 'INSFLNAM', 'INSGRID', 'INSGRNAM',
   'INSGRROT', 'INSGRWL0', 'INSGRRES', 'INSPOFPI', 'INSPOROT', 'INSFPZ',
   'INSFPWL', 'INSFPDWL', 'INSFPORD', 'INSCALST', 'INSCALID', 'INSCALNM',
   'NPOINTS', 'FMINIMUM', 'QUANT025', 'QUANT159', 'QUANT250', 'QUANT500',
   'QUANT750', 'QUANT841', 'QUANT975', 'FMAXIMUM', 'ROBUSTSTD']

Let's display the values of a few of keywords: ``QUANT500`` (the image median),
``QUANT975`` (the quantile 0.975 of the image), and ``ROBUSTSTD`` (the robust
standard deviation of the image):

::

   (filabres) $ filabres -lc bias -k quant500 -k quant975 -k robuststd
                                                                                            file   QUANT500   QUANT975  ROBUSTSTD
   1    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:27:48-cal-krek.fits  666.00000  686.00000  11.11950 
   2    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:29:09-cal-krek.fits  666.00000  687.00000  10.37820 
   3    /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170224-21:30:31-cal-krek.fits  666.00000  683.00000  10.37820 
   ...
   ...
   824  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:16:48-cal-lilj.fits  658.00000  680.00000  11.11950 
   825  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:17:24-cal-lilj.fits  658.00000  680.00000  11.11950 
   826  /Volumes/NicoPassport/CAHA/CAFOS2017/171230_t2_CAFOS/caf-20171229-10:18:00-cal-lilj.fits  658.00000  680.00000  11.11950 

Note that each keyword is preceded by ``-k`` (following the astropy convention
for the fitsheader utility).

If instead of using ``-k`` you use ``-ks``, the list will be sorted according
to the selected keywords (several keys can be used for a hierarchical sorting):

::

   (filabres) $ filabres -lc bias -k quant500 -k quant975 -ks robuststd
            file   QUANT500   QUANT975  ROBUSTSTD
   456  /Volumes/NicoPassport/CAHA/CAFOS2017/170929_t2_CAFOS/caf-20170929-13:52:35-cal-bias.fits  661.40002  666.70001  2.81693  
   206  /Volumes/NicoPassport/CAHA/CAFOS2017/170526_t2_CAFOS/caf-20170526-15:44:34-cal-boeh.fits  667.00000  683.00000  6.67170  
   207  /Volumes/NicoPassport/CAHA/CAFOS2017/170526_t2_CAFOS/caf-20170526-15:45:45-cal-boeh.fits  667.00000  683.00000  6.67170  
   ...
   ...
   241  /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:12:14-cal-bomd.fits  723.00000  776.00000  25.94550 
   245  /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-13:17:01-cal-bomd.fits  723.00000  776.00000  25.94550 
   311  /Volumes/NicoPassport/CAHA/CAFOS2017/170628_t2_CAFOS/caf-20170628-17:29:10-cal-pelm.fits  693.00000  729.00000  25.94550 

Note that now the column ``ROBUSTSTD`` apears sorted.

Is is also possible to generate plots with the selected keywords. For that
purpose, employ the ``-pxy`` argument:

::

   (filabres) $ filabres -lc bias -k mjd-obs -k quant500 -k quant975 -ks robuststd -pxy


Is there something wrong with the image classification?
=======================================================

Before moving to the reduction of the calibration images, it is important to
check the image classification. In this sense, a few image types should be
revised, as shown in the following subsections.

Wrong instrument
----------------

Unclassified
------------

These are images that could not be classified according to the rules
defined in ``configuration_cafos.yaml``:

::

   (filabres) $ filabres -lc unclassified
                                                                                          file IMAGETYP              OBJECT
   1  /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-18:44:14-tst-test.fits  shift    [focus] Telescope 
   2  /Volumes/NicoPassport/CAHA/CAFOS2017/170505_t2_CAFOS/caf-20170506-02:53:44-tst-test.fits  shift    [focus] Telescope 
   3  /Volumes/NicoPassport/CAHA/CAFOS2017/170601_t2_CAFOS/caf-20170601-14:00:42-sci-etac.fits  shift    ETALON_calibration
   4  /Volumes/NicoPassport/CAHA/CAFOS2017/170628_t2_CAFOS/caf-20170628-16:26:53-sci-etac.fits  shift    ETALON_calibration
   5  /Volumes/NicoPassport/CAHA/CAFOS2017/170628_t2_CAFOS/caf-20170628-16:35:52-sci-etac.fits  shift    ETALON_calibration
   6  /Volumes/NicoPassport/CAHA/CAFOS2017/170807_t2_CAFOS/caf-20170807-21:10:39-cal-schn.fits  shift    [focus] Telescope 
   Total: 6 files

Only 6 images appear in this category. You can display all of them in
sequence adding the argument ``-pi`` (plot image):

::

   (filabres) $ filabres -lc unclassified -pi

You can safely ignore these images.

Ignored
-------

Wrong bias
----------

Wrong flat-imaging
------------------

Wrong flat-spectroscopy
-----------------------

Wrong arc
---------

Wrong science-imaging
---------------------

Wrong science-spectroscopy
--------------------------

Update the file ``image_header_corrections.yaml``
=================================================
.. warning::

   Wildcards are allowed for ``files:`` but not for ``night:``.

And repeat image classification!


