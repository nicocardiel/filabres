.. filabres documentation master file, created by
   sphinx-quickstart on Wed Mar  4 20:10:29 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Filabres's documentation!
====================================

**Filabres** started in 2019 as a joint effort of the `Calar Alto Observatory
<http://w3.caha.es/>`_ (especially Santos Pedraz and Jesús Aceituno), the
`Spanish Virtual Observatory <https://svo.cab.inta-csic.es/>`_ (Enrique Solano,
José Manuel Alacid and Miriam Cortés), and the `Physics of the Earth and
Astrophysics Department
<https://www.ucm.es/fisica_de_la_tierra_y_astrofisica/>`_ at the Universidad
Complutense de Madrid (Nicolás Cardiel, Sergio Pascual, Enrique Galcerán and
Jaime Alonso), and the collaboration of the `Instituto de Física de
Cantabria <https://ifca.unican.es/>`_
(Maite Ceballos), with the main goal of providing useful reduced images through
the Calar Alto Archive hosted at http://caha.sdc.cab.inta-csic.es/calto/.

Although this software package was initially created with the idea of
performing the automatic reduction of direct images obtained with the
instrument CAFOS, placed at the 2.2 m telescope of the Calar Alto Observatory,
**filabres** has been designed to allow the future inclusion of additional
observing modes and instruments.

The typical workflow with **filabres** consists of the following steps:

1. Image classification (bias, flat-imaging, arc, science-imaging, etc.)

2. Reduction of calibration images (bias, flat-imaging) and generation
   of combined master calibrations as a function of the modified Julian Date.

3. Basic reduction of individual science images, making use of the corresponding
   master calibrations (closest in time to the observation of the science
   target). The main reduction steps considered here are:

   - bias subtraction

   - flatfielding of the images

   - astrometric calibration (performed with the help of additional software
     tools provided by `Astrometry.net <http://astrometry.net/doc/readme.html>`_
     and by `AstrOmatic.net <https://www.astromatic.net/>`_)

An example of use of **filabres** with CAFOS data from 2017 is illustrated in
this documentation.

----

.. only:: html

   **Document index:**

.. toctree::
   :maxdepth: 2

   installation
   setup
   check
   classification
   bias
   flat-imaging
   science-imaging
   lsss-test

----

Software repository: https://github.com/nicocardiel/filabres

Developers and maintainers: Nicolás Cardiel (cardiel@ucm.es) and Sergio Pascual
(sergiopr@fis.ucm.es)
