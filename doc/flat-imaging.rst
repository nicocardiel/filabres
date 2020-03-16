.. _flat-imaging_reduction:

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


(Work in progress)

Database of flat-imaging master frames
======================================

Checking the flat-imaging reduction
===================================

Removing invalid reduced flat-imaging
=====================================

