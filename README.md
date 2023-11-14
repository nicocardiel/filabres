# filabres

Automatic Data Reduction Pipeline for CAHA data.

Filabres is embedded in a joint effort of the Calar Alto Observatory 
(especially Santos Pedraz and Jesús Aceituno), the Spanish Virtual Observatory
 (Enrique Solano, José Manuel Alacid and Miriam Cortés), and the Physics of 
 the Earth and Astrophysics Department at the Universidad Complutense de 
 Madrid (Nicolás Cardiel, Sergio Pascual, Enrique Galcerán and Jaime 
 Hernández), and the collaboration of the Instituto de Física de Cantabria 
 (Maite Ceballos), with the main goal of providing useful reduced images 
 through the Calar Alto Archive hosted at 
 http://caha.sdc.cab.inta-csic.es/calto/.

Although this software package has been initially created with the idea of 
performing the automatic reduction of direct images obtained with the 
instrument CAFOS, placed at the 2.2 m telescope of the Calar Alto 
Observatory, filabres has been designed to allow the future inclusion of 
additional observing modes and instruments.

## Installing the code

In order to keep your current Python installation clean, it is highly
recommended to first build a new Python 3 *virtual environment*.

```shell
$ python3 -m venv venv_filabres
$ . venv_filabres/bin/activate
(venv_filabres) $
```

We recommend installing the latest stable version, which is available via
the [PyPI respository](https://pypi.org/project/filabres/):

```shell
(venv_filabres) $ pip install filabres
```

The latest development version is available through [GitHub](https://github.com/nicocardiel/filabres):

```shell
(venv_filabres) $ pip install git+https://github.com/nicocardiel/filabres.git@main#egg=filabres
```

## Usage

See full documentation at https://filabres.readthedocs.io/

Developers and maintainers: Nicolás Cardiel (cardiel@ucm.es) and 
Sergio Pascual (sergiopr@fis.ucm.es)
