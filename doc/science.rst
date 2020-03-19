.. _reduction_of_science_images:

***************************
Reduction of science images
***************************

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

Considering that this number is very high, it is advisable to start the
reduction of these scientific images by constraining the process to images
belonging to a single night. In particular, we are going to illustrate the
procedure using images corresponding to the first night ``170225_t2_CAFOS``.
For this example, we are using enhanced verbosity (argument ``-v/--verbose``)
and indicate that we want an interactive execution (argument
``-i/--interactive``; this is going to stop the reduction to show some
intermediate plots and results):

::

  $ filabres -rs science-imaging -n 170225* -v -i

(Work in progress)

Database of reduced science-imaging frames
==========================================

Contrary to what is done with the reduced calibration, where all the reduced
calibration frames are stored in a single file
``filabres_db_cafos_<calibration>.json`` (where ``<calibration>`` is ``bias``
or ``flat-imaging``), in the case of the science images, the results of the
reduction are separately stored in independent files
``filabres_db_science-imaging.json`` located within the subdirectory reserved
for each observing night under the ``science-imaging`` subdirectory tree.

(Work in progress)

Checking the science-imaging reduction
======================================

(Work in progress)

::

  $ filabres -lr science-imaging -k all
  $ filabres -lr science-imaging -k ierr_bias -k ierr_flat

Removing invalid reduced science-imaging frames
===============================================

(Work in progress)
