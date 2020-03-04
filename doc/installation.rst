.. _filabres_installation:

*************************
**filabres** installation
*************************


.. warning::

   **filabres** is a Python package: Python 3.7 or greater is recommended.

   Although you probably already have a python interpreter installed in your
   system, it is a good idea to follow the instructions given in this section.

   As explained below, the use of conda will help you to isolate the
   installation of a particular set of python interpreter and auxiliary
   packages in something called *an environment*, which will prevent the
   collision of the particular version of the python interpreter and python
   packages with any previous python installation in your computer.

Our recommendation: to use **Miniconda** to handle the installation of the
proper Python interpreter and some auxiliary packages. Note that **Miniconda**
and **Anaconda** are not the same thing. Actually, **Miniconda** is a smaller
alternative to **Anaconda**. **Miniconda** just contains the conda package
manager and python.  After installing this, you can install individual python
packages easily using conda (see below). On the other hand, **Anaconda**
contains not only conda and python, but also a large collection of additional
python packages. By installing simply **Miniconda** you reduce the amount of
packages preinstalled in your system (after installing **Miniconda** it is
possible to install **Anaconda** by executing conda install anaconda).

Miniconda installation
----------------------

Visit the `Miniconda webpage <https://docs.conda.io/en/latest/miniconda.html>`_ and download the installer corresponding to your operative system (and, preferably, Python 3.7, which is the python version employed to develop the code).

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
`filabres`, can be created indicating the use of the last version of Python 3,
together with some additional packages:

::

   $ conda create --name filabres python=3 \
   astropy \
   ipython \
   matplotlib \
   numpy \
   PyYaml \


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


Installing the development version of **filabres**
--------------------------------------------------

The development version is the most updated working version of the code.

::

Activate the environment:

::

   $ conda activate filabres
   (filabres) $


Download the development version using git:

::

   (filabres) $ git clone https://github.com/nicocardiel/filabres.git
   (filabres) $ cd filabres

Build and install the code:

::

   (filabres) $ python setup.py build
   (filabres) $ python setup.py install


If you have **filabres** already installed in your system, but want to update
the code with the latest version, you need to move to the same directory where
you previously cloned the repository, pull the latest changes in the code, and
reinstall it:

::

   (filabres) $ cd filabres
   (filabres) $ git pull
   (filabres) $ python setup.py build
   (filabres) $ python setup.py install


Check that **filabres** works:

::

   (filabers) $ filabres-version
   Version: 0.9.0
