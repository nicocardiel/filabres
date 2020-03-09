.. _image_classification:

********************
Image classification
********************

Initialize the auxiliary image databases
========================================

The next step is the classification of the different images. This
classification will take place by generating a local database (a JSON file
called ``imagedb.json``) for each observing night. For this purpose,
**filabres** will follow the rules provided in the instrument configuration
file ``configuration_cafos.yaml``. In its first hierarchical level, this file
defines the following keys: ``instname``, ``version``, ``requirements``,
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
    considered in **filabres**.

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

Classify the images
===================

Examine the image classification
================================

Update the file ``image_header_corrections.yaml``
=================================================
.. warning::

   Wildcards are allowed for ``files:`` but not for ``night:``.

And repeat image classification!


