.. _filabres_installation:

*************************
**Filabres** installation
*************************

.. note::

   **Filabres** is a Python package: Python 3.7 or greater is recommended.

   Although you probably already have a Python interpreter installed in your
   system, it is a good idea to follow the instructions given in this section.

   As explained below, the use of ``conda`` will help you to isolate the
   installation of a particular set of Python interpreter and auxiliary
   packages in something called an *environment*, which will prevent the
   collision of the particular version of the Python interpreter and Python
   packages with any previous Python installation in your computer.

Our recommendation: to use **Miniconda** to handle the installation of the
proper Python interpreter and some auxiliary packages. Note that **Miniconda**
and **Anaconda** are not the same thing. Actually, **Miniconda** is a smaller
alternative to **Anaconda**. **Miniconda** just contains the conda package
manager and Python.  After installing this, you can add individual Python
packages easily using ``conda``. On the other hand, **Anaconda**
contains not only ``conda`` and Python, but also a large collection of
additional Python packages. By installing simply **Miniconda** you reduce the
amount of packages preinstalled in your system (after installing **Miniconda**
it is possible to install **Anaconda** by executing ``conda install anaconda``).


**Conda** installation
----------------------

Visit the `Miniconda webpage <https://docs.conda.io/en/latest/miniconda.html>`_
and download the installer corresponding to your operative system (and,
preferably, Python 3.7, which is the Python version employed to develop the code).

If you have updated the ``$PATH`` system variable during the miniconda or conda
installation, you can call conda commands directly in the shell, like this:

::

   $ conda info

If not, you will need the add the path to the command, like:

::

  $ /path/to/conda/bin/conda info


In this guide we will write the commands without the full path, for simplicity.


**Create a conda environment**

The new environment, which arbitrarily (and not surprisingly) will be called
``filabres``, can be created indicating the use of the last version of Python 3,
together with some additional packages:

::

   $ conda create --name filabres python=3 \
   astropy \
   ipython \
   matplotlib \
   numpy \
   pandas \
   python-dateutil \
   PyYaml \
   scipy \
   setuptools

and answer ``y`` to the question ``Proceed ([y]/n)?``

**Activate the environment**

::

   $ conda activate filabres

which yields a different system prompt to the user:

::

   (filabres) $ 


**Deactivate the environment**
  
To exit the environment is enough to exit the terminal or run the following
command:

::
  
   (filabres) $ conda deactivate
   $

**Removing the environment**

If at a given point you need to remove the environment, deactivate that
environment and remove it through conda:

::

   (filabres) $ conda deactivate
   $ conda remove --name filabres --all

To verify that the environment was removed, execute:

::

   $ conda info --envs

If you want to know more about **conda**, have a look to the `on-line
documentation <https://docs.conda.io/projects/conda/en/latest/index.html>`_.


Installing the development version of **filabres**
--------------------------------------------------

The development version is the most updated working version of the code. It
can be easily installed in your system by executing the following steps:

1. Activate the environment:

  ::

     $ conda activate filabres
     (filabres) $


2. Download the development version using git:

  ::

     (filabres) $ git clone https://github.com/nicocardiel/filabres.git
     (filabres) $ cd filabres

3. Build and install the code:

  ::

     (filabres) $ python setup.py build
     (filabres) $ python setup.py install


  If you have **filabres** already installed in your system, but want to update
  the code with the latest version, you need to move to the same directory where
  you previously cloned the repository, pull the latest changes of the code, and
  reinstall it:

  ::

     (filabres) $ cd filabres
     (filabres) $ git pull
     (filabres) $ python setup.py build
     (filabres) $ python setup.py install

4. Install some additional Python packages:

  ::

     (filabres) $ conda install -c conda-forge pyvo

5. Check that **filabres** works:

  ::

     (filabres) $ filabres-version
     Version: 0.9.0

  Note that your version can be different to the one shown above.

  To display a help message on the terminal use the argument ``-h/--help``:

  ::

     (filabres) $ filabres -h

Required additional software packages
-------------------------------------

The astrometric calibration is delegated to two well-known software packages
specially suited for this task:

- `Astrometry.net <http://astrometry.net/doc/readme.html>`_: determines an
  initial astrometric calibration using a gnomic projection ``RA---TAN`` and
  ``DEC--TAN``, with SIP (Simple Imaging Polynomial) distortions. The
  required binaries are:

   - ``build-astrometry-index``: computes a suitable index file (containing
     hash codes of typically sets of four stars) that facilitates the alignment
     of the requested image. Note that **filabres** does not use the
     pre-computed index files provided by Astrometry.net, but uses index files
     especially suited for each region of the sky covered by the science images.
     These files are built from GAIA data downloaded from the internet while
     executing the code. Within each night, a database is created with the
     regions of the sky covered by the different images. This avoids the need
     to regenerate the index files for images that correspond to close
     pointings.

   - ``solve-field``: determines the astrometric calibration using the index
     file previously computed.

  The initial astrometric calibration provides typical errors of the order
  of the seeing, although we have checked that these errors are larger at
  the image borders in a systematic way, probably because the distortion is
  determined using a second-order polynomial, which is not good enough.
  For that reason, this astrometric calibration is refined by using
  the AstrOmatic.net tools.

- `AstrOmatic.net <https://www.astromatic.net/>`_: ``sextractor`` and ``scamp``
  are employed to detect the image sources and perform a refined astrometric
  calibration, using the TPV World Coordinate System to map the image
  distortions. The initial WCS solution provided by the Astrometry.net software
  allows ``scamp`` to determine a much better WCS solution by setting the
  TPV polynomial degrees to 3, leading to typical errors within a fraction of
  a pixel. Again, GAIA data is retrieved from the internet to carry out this
  astrometric calibration.

.. warning::

  Note that the astrometric calibration is performed using GAIA data
  downloaded from the internet on real time while executing **filabres**.
  This means that a live internet connection is required for the code to
  work properly.

Installing Astrometry.net
.........................

For the installation of this code you can follow the instructions given in
`Building/installing the Astrometry.net code
<http://astrometry.net/doc/build.html>`_, or make use of **conda** to install
it within the ``filabres`` environment:

::

   $ conda activate filabres
   (filabres) $ conda install -c conda-forge astrometry

Installing AstrOmatic.net
.........................

Here you can follow the instructions provided in the official web pages for
`sextractor <https://www.astromatic.net/software/sextractor>`_ and
`scamp <https://www.astromatic.net/software/scamp>`_, or make use of **conda**
to install both programs within the ``filabres`` environment:

::

   $ conda activate filabres
   (filabres) $ conda install -c conda-forge astromatic-source-extractor
   (filabres) $ conda install -c conda-forge astromatic-scamp

