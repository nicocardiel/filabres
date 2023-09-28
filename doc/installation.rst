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
to download the installer appropriate for your operating system. Although the original code was developed using Python 3.7, ensure you select a recent Python version.

If you have updated the ``$PATH`` system variable during the **Miniconda** or
**Anaconda** installation, you can call ``conda`` commands directly in the
shell, like this:

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
  seaborn \
  setuptools

and answer ``y`` to the question ``Proceed ([y]/n)?``

**Activate the environment**

::

  $ conda activate filabres

which yields a different system prompt to the user:

::

  (filabres) $ 

**Installing additional Python packages**

The Gaia data employed to determine the astrometric calibration requires the
use of the ``astroquery`` package, which can be easily installed with
``conda``:

::

  (filabres) $ conda install -c conda-forge astroquery

**Deactivate the environment**
  
To exit the environment is enough to exit the terminal or run the following
command:

::
  
  (filabres) $ conda deactivate
  $

**Removing the environment**

If at a given point you need to remove the environment, deactivate that
environment and remove it through ``conda``:

::

  (filabres) $ conda deactivate
  $ conda remove --name filabres --all

To verify that the environment was removed, execute:

::

  $ conda info --envs

If you want to know more about ``conda``, have a look to the `on-line
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

    (filabres) $ pip install -e .


  If you have **filabres** already installed in your system, but want to update
  the code with the latest version, you need to move to the same directory where
  you previously cloned the repository, pull the latest changes of the code, and
  reinstall it:

  ::

    (filabres) $ cd filabres
    (filabres) $ git pull
    (filabres) $ pip install -e .

4. Check that **filabres** works:

  ::

    (filabres) $ filabres-version
    Version: 1.3.0

  Note that your version can be different to the one shown above.

  To display a help message on the terminal use the argument ``-h/--help``:

  ::

    (filabres) $ filabres -h

Required additional software packages
-------------------------------------

The astrometric calibration is delegated to two well-known software packages
specially suited for this task:

- `Astrometry.net <http://astrometry.net/doc/readme.html>`_: determines an
  initial astrometric calibration using a gnomic projection ``RA---TAN-SIP``
  and ``DEC--TAN-SIP``, with SIP (Simple Imaging Polynomial) distortions. The
  required binaries are ``build-astrometry-index`` and ``solve-field``.  This
  initial astrometric calibration is refined by using the AstrOmatic.net tools.

- `AstrOmatic.net <https://www.astromatic.net/>`_: ``sextractor`` and ``scamp``
  are employed to detect the image sources and perform a refined astrometric
  calibration, using the TPV World Coordinate System to map the image
  distortions.

.. warning::

  Note that the astrometric calibration is performed using GAIA data
  downloaded from the internet on real time while executing **filabres**.
  This means that a live internet connection is required for the code to
  work properly.

Installing Astrometry.net tools
...............................

For the installation of this code you can use ``conda`` to install within
the ``filabres`` environment:

::

  (filabres) $ conda install -c conda-forge astrometry

or follow the instructions given in
`Building/installing the Astrometry.net code
<http://astrometry.net/doc/build.html>`_.

In macOS it is also possible to use the package manager
`Homebrew <https://brew.sh/>`_:

::

  (filabres) $ brew install astrometry-net

Installing AstrOmatic.net tools
...............................

The initial astrometric solution found with the Astrometry.net tools can be
refined using the AstrOmatic.net programs ``sextractor`` and ``scamp``. Both
codes can be installed using ``conda``:

::

  (filabres) $ conda install -c conda-forge astromatic-source-extractor
  (filabres) $ conda install -c conda-forge astromatic-scamp

or follow the instructions provided in the official web pages for
`sextractor <https://www.astromatic.net/software/sextractor>`_ and
`scamp <https://www.astromatic.net/software/scamp>`_.

If either of these two programs (``sextractor`` or ``scamp``) is not installed,
the refinement process is skipped during the astrometric calibration.
