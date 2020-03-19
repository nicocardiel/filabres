.. _reduction_of_science_imaging_frames:

***********************************
Reduction of science-imaging frames
***********************************

.. note::

   The reduction of science images is carry out individually, i.e., the
   scientific images are not combined within any time span prior to the
   reduction process (in fact, the value of ``maxtimespan_hours`` is set to
   zero in the file ``configuration_cafos.yaml``).

There are many individual images classified as ``science-imaging``:

::

  $ filabres -lc science-imaging
  ...
  ...
  Total: 4931 files

Only in the first night we have 48 images:

::

  $ filabres -lc science-imaging -n 170225*
                                                                                          file
  1   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-18:59:12-sci-krek.fits
  2   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-19:01:30-sci-krek.fits
  3   /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-19:04:18-sci-krek.fits
  ...
  ...
  46  /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-22:17:06-sci-krek.fits
  47  /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-22:18:58-sci-krek.fits
  48  /Volumes/NicoPassport/CAHA/CAFOS2017/170225_t2_CAFOS/caf-20170225-22:20:27-sci-krek.fits
  Total: 48 files

Considering the large number of images, it is advisable to start the reduction
of these scientific images by constraining the process to a subset of images.
In this sense, we can choose between the different options shown below. Note
that in all the following examples we are using enhanced verbosity (argument
``-v/--verbose``) and an interactive execution (argument
``-i/--interactive``; this is going to stop the reduction to show some
intermediate plots and results).

The different possibilities are (do not try these examples yet! their purpose
here is simply to illustrate the different approaches):

1. Reduce a single ``science-imaging`` image using the argument ``-n/--night``
   for the night and the argument ``--filename`` followed by the explicit name
   of the original FITS file (*without the file path*). For example, the first
   file of the first night is reduced executing:

   ::

     $ filabres -rs science-imaging -v -i -n 170225* --filename caf-20170225-18:59:12-sci-krek.fits

   Here we have specified the reduction step ``-rs science-imaging``, the use
   of enhanced verbosity ``-v``, the interactive execution of the program
   ``-i``, the observing night ``-n 170225*``, and the specific file to be
   reduced ``--filename caf-20170225-18:59:12-sci-krek.fits``.

2. Reduce all the ``science-imaging`` files within a given night. In this case
   just omit ``--filename <file>``. Only the night must be specified:

   ::

     $ filabres -rs science-imaging -v -i -n 170225*

   In this case you will probably prefer to execute the reduction of the files
   without ``-i``.

3. Reduce all the ``science-imaging`` files of all nights: if a specific night
   is not given, **filabres** will try to reduce all the images of this type,
   independently of the observing night:

   ::

     $ filabres -rs science-imaging -v -i

   In this case you will also prefer to execute the reduction of the files
   without ``-i`` (and also without ``-v``; relevant information concerning the
   reduction of each individual file is conveniently stored).

.. _reduction_of_a_single_science-imaging_frame:

Reduction of a single science-imaging frame
===========================================

(Work in progress)

::

  $ filabres -rs science-imaging -v -i -n 170225* --filename caf-20170225-18:59:12-sci-krek.fits

.. _database_of_reduced_science-imaging_frames:

Database of reduced science-imaging frames
==========================================

Contrary to what is done with the reduced calibrations, where all the
information is stored in a single database
``filabres_db_cafos_<calibration>.json`` (where ``<calibration>`` is ``bias``
or ``flat-imaging``), in the case of the science images, that information is
separately stored in independent files ``filabres_db_science-imaging.json``
located within the subdirectory reserved for each observing night under the
``science-imaging`` subdirectory tree. In addition to this, within the same
subdirectory tree, a specific subdirectory is also created for each reduced
image, where **filabres** stores additional auxiliary files created during the
data reduction.

(Work in progress)

.. _checking_the_science-imaging_reduction:

Checking the science-imaging reduction
======================================

(Work in progress)

::

  $ filabres -lr science-imaging -k all
  $ filabres -lr science-imaging -k ierr_bias -k ierr_flat

Removing invalid reduced science-imaging frames
===============================================

(Work in progress)
