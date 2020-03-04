.. filabres documentation master file, created by
   sphinx-quickstart on Wed Mar  4 20:10:29 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to filabres's documentation!
====================================

This is the documentation for filabres (version |version|).

This software has been created with the idea of performing the automatic
reduction of images obtained with the instrument CAFOS, placed at the 2.2 m
telescope of the Calar Alto Observatory.  The goal is to provide useful
reduced images through Calar Alto Archive hosted at
http://caha.sdc.cab.inta-csic.es/calto/.

The project is a joint effort of the `Calar Alto Observatory
<http://w3.caha.es/>`_ (specially Santos Pedraz and Jesús Aceituno), 
the `Spanish Virtual Observatory
<https://svo.cab.inta-csic.es/>`_ (Enrique Solano, José Manuel Alacid and
Miriam Cortés), and the `Physics of the Earth and
Astrophysics Department
<https://www.ucm.es/fisica_de_la_tierra_y_astrofisica/>`_ at the Universidad
Complutense de Madrid (Nicolás Cardiel, Enrique Galcerán and Jaime Hernández).

At present, the code performs the following tasks:

- Image classification (bias, flat-imaging, science-imaging, etc.)

- Reduction of calibration images (bias, flat-imaging, etc.) and generation
  of combined master calibrations as a function of the modified Julian Date.

- Basic reduction of individual science images, making use of the corresponding
  master calibrations (closest in time to the observation of the science
  target).  The main reduction steps are:

  - bias subtraction

  - flatfielding of the images

  - astrometric calibration


Maintainer: Nicolás Cardiel (cardiel@ucm.es)

.. only:: html

   Document index:

.. toctree::
   :maxdepth: 2

   installation
