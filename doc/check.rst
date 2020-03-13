.. _initial_image_check:

*******************
Initial image check
*******************

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
   Press <ENTER> to display duplicate files...

At this point the program has revealed that there are repeated files. The
duplicate cases are displayed after pressing ``<ENTER>``

::

   * File caf-20170505-13:42:00-cal-reba.fits appears in:
   /Users/cardiel/CAFOS2017/170505_t2_CAFOS/caf-20170505-13:42:00-cal-reba.fits
   /Users/cardiel/CAFOS2017/170506_t2_CAFOS/caf-20170505-13:42:00-cal-reba.fits
   /Users/cardiel/CAFOS2017/170507_t2_CAFOS/caf-20170505-13:42:00-cal-reba.fits

   * File caf-20170505-21:30:03-sci-agui.fits appears in:
   /Users/cardiel/CAFOS2017/170505_t2_CAFOS/caf-20170505-21:30:03-sci-agui.fits
   /Users/cardiel/CAFOS2017/170506_t2_CAFOS/caf-20170505-21:30:03-sci-agui.fits

   * File caf-20170505-10:08:36-cal-agui.fits appears in:
   /Users/cardiel/CAFOS2017/170505_t2_CAFOS/caf-20170505-10:08:36-cal-agui.fits
   /Users/cardiel/CAFOS2017/170506_t2_CAFOS/caf-20170505-10:08:36-cal-agui.fits
   /Users/cardiel/CAFOS2017/170507_t2_CAFOS/caf-20170505-10:08:36-cal-agui.fits
   ...
   ...
   * File caf-20171225-19:28:31-cal-bard.fits appears in:
   /Users/cardiel/CAFOS2017/171217_t2_CAFOS/caf-20171225-19:28:31-cal-bard.fits
   /Users/cardiel/CAFOS2017/171225_t2_CAFOS/caf-20171225-19:28:31-cal-bard.fits

   * File caf-20171225-19:42:55-cal-bard.fits appears in:
   /Users/cardiel/CAFOS2017/171217_t2_CAFOS/caf-20171225-19:42:55-cal-bard.fits
   /Users/cardiel/CAFOS2017/171225_t2_CAFOS/caf-20171225-19:42:55-cal-bard.fits
   * program STOP

The detailed examination of the above output reveals that:

- the files ``caf-20170505-*`` are duplicated in subdirectory night
  ``170506_t2_CAFOS``

- the files ``caf-20170505-*`` are duplicated in subdirectory night
  ``170507_t2_CAFOS``

- all the files in ``171219_t2_CAFOS`` are duplicated calibrations from
  ``171218_t2_CAFOS``

- the files ``caf-20171225-*`` are duplicated in subdirectory night
  ``171217_t2_CAFOS``

Updating ``ignored_images.yaml``
================================

The best way to deal with these duplicated files is to insert them in the
auxiliary file ``ignored_images.yaml``. For this particular example, the
contents of this file are:

.. literalinclude:: ignored_images_v1.yaml
   :linenos:
   :lineno-start: 1

Ignoring the initial comment lines (starting by ``#``), 
there are four blocks separated by ``---`` (the YAML block separator).
**Important**: the separator must not appear before the first block nor
after the last block. Within each
block, the following arguments must be provided:

- ``night``: observing night. Note that wildcards can not be used here,
  although the same night label can appear in different blocks.

- ``enabled``: this key indicates that the files included in this block are
  going to be ignored. Setting this key to ``False`` allows to disable 
  a particular block without the need of removing it from this file.

- ``files``: is the list of files to be ignored within the specified night. 
  The list of files can be provided by given the name of each file in separate
  line, preceded by an indented ``-`` symbol. Wildcards are valid here.

Re-check the image tree
=======================

After the update of the file ``ignored_images.yaml``, the execution of the
initial check must indicate that there are no repeated files:

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
   There are not repeated files
   * program STOP

