.. _tutorial_cafos2017:

*************************
Tutorial: CAFOS 2017 data
*************************

.. warning::

   It is recommedable to run the code from an empty directory.

Activate the conda environment ``filabres`` and check that the software is
available:

::

   $ conda activate filabres
   (filabres ) $ filabres-version
   0.9.0

Note that your version can be different to the one shown above.

Create ``setup_filabres.yaml``
==============================

Before executing **filabres**, make sure that there is a file in the current
directory called ``setup_filabres.yaml`` (YAML is a human-readable
data-serialization language commonly used for configuration files).
This file simply contains a few definitions:

- ``instrument``: the instrument name

- ``datadir``: the directory where the original (raw data) FITS files are
  stored

- ``image_corrections_file``: the name of an auxiliary YAML file that contains
  corrections for the image classfications (which will be explaned below).

For illustration, the contents of ``setup_filabres.yaml`` should be something
like:

::

   instrument: cafos
   datadir: /Users/cardiel/CAFOS2017
   image_corrections_file: image_corrections.yaml

Note that under the directory ``datadir`` there must exist a subdirectory tree
where the origial FITS files are segregated in different nights, i.e.,

::

   (filabres) $ ls /Users/cardiel/CAFOS2017
   170225_t2_CAFOS/ 170524_t2_CAFOS/ 170807_t2_CAFOS/ 171108_t2_CAFOS/
   170226_t2_CAFOS/ 170525_t2_CAFOS/ 170809_t2_CAFOS/ 171116_t2_CAFOS/
   170319_t2_CAFOS/ 170526_t2_CAFOS/ 170811_t2_CAFOS/ 171120_t2_CAFOS/
   170331_t2_CAFOS/ 170527_t2_CAFOS/ 170825_t2_CAFOS/ 171121_t2_CAFOS/
   170403_t2_CAFOS/ 170528_t2_CAFOS/ 170903_t2_CAFOS/ 171209_t2_CAFOS/
   170408_t2_CAFOS/ 170601_t2_CAFOS/ 170918_t2_CAFOS/ 171217_t2_CAFOS/
   170420_t2_CAFOS/ 170602_t2_CAFOS/ 170926_t2_CAFOS/ 171218_t2_CAFOS/
   170422_t2_CAFOS/ 170621_t2_CAFOS/ 170928_t2_CAFOS/ 171219_t2_CAFOS/
   170502_t2_CAFOS/ 170627_t2_CAFOS/ 170929_t2_CAFOS/ 171221_t2_CAFOS/
   170505_t2_CAFOS/ 170628_t2_CAFOS/ 171002_t2_CAFOS/ 171223_t2_CAFOS/
   170506_t2_CAFOS/ 170629_t2_CAFOS/ 171008_t2_CAFOS/ 171225_t2_CAFOS/
   170507_t2_CAFOS/ 170713_t2_CAFOS/ 171011_t2_CAFOS/ 171228_t2_CAFOS/
   170517_t2_CAFOS/ 170720_t2_CAFOS/ 171015_t2_CAFOS/ 171230_t2_CAFOS/
   170518_t2_CAFOS/ 170724_t2_CAFOS/ 171016_t2_CAFOS/
   170519_t2_CAFOS/ 170731_t2_CAFOS/ 171101_t2_CAFOS/

.. note::

   The original FITS files are not modified by **filabres**.
   This program copies all the required files to the working directory in
   order to keep the original files safe from accidental overwritting or
   deletion. In this sense, the working directory should be different
   from ``datadir``.

Initial image check
===================

Before starting with the image classification, it is important to double check
that there are no duplicate original FITS images within the ``datadir`` tree.
This can be easily checked using:

::

   (filabres) $ filabres --check
   Night 170225_t2_CAFOS -> number of files:   140 --> TOTAL:   140
   Night 170226_t2_CAFOS -> number of files:    55 --> TOTAL:   195
   Night 170319_t2_CAFOS -> number of files:   149 --> TOTAL:   344
   Night 170331_t2_CAFOS -> number of files:   119 --> TOTAL:   463
   Night 170403_t2_CAFOS -> number of files:   336 --> TOTAL:   799
   Night 170408_t2_CAFOS -> number of files:   153 --> TOTAL:   952
   ...
   ...
   Night 171221_t2_CAFOS -> number of files:   185 --> TOTAL:  8839
   Night 171223_t2_CAFOS -> number of files:    74 --> TOTAL:  8913
   Night 171225_t2_CAFOS -> number of files:    86 --> TOTAL:  8999
   Night 171228_t2_CAFOS -> number of files:    50 --> TOTAL:  9049
   Night 171230_t2_CAFOS -> number of files:   383 --> TOTAL:  9432
   WARNING: There are repeated files!
   Press <ENTER> to continue...

At this point the program has revealed that there are repeated files.

Initialize the auxiliary image databases
========================================

Classify the images
-------------------

Examine the image classification
--------------------------------

Reduction of calibration images
===============================


Bias images
-----------

Flat images
-----------

Reduction of science images
===========================

