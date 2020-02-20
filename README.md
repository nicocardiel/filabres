# filabres

Automatic Data Reduction Pipeline for CAHA data.

To install the code, clone the repository and execute:
```
$ cd filabres
$ python setup.py build
$ python setup.py install
```

It is recommendable to run the code from an empty directory.

### Create `setup_filabres.yaml`
Before executing filabres, make sure that there is a file in the 
current directory called `setup_filabres.yaml`. This file simply contains
a couple of definitions: the instrument name and the directory where
the raw FITS files are stored. For example:
```
instrument: cafos
datadir: /Users/cardiel/CAFOS2017
```
Note that under the directory `datadir` there must exist a subdirectory
tree where the FITS files are segregated in different nights, i.e.,
```
$ ls /Users/cardiel/CAFOS2017
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
```  

### Initialize the auxiliary image databases
Execute the program to initialize the auxiliary image databases:
```
$ filabres -rs initialize
```
The `-rs/--reduction_step` argument indicates the reduction step that must
be executed by the program.

The previous command will initialize the auxiliary image databases for
all the available nights under the `datadir` directory. If you are
interested in initializing only a subsets of nights it is possible to
define them with the `-n/--night` argument:
```
$ filabres -n 17????_t2_CAFOS -rs initialize
```

The previous command generates a subdirectory `lists` in the current
directory, with a tree of observing nights. Within each night a file called
`imagedb_cafos.json` stores the image classification (i.e., bias, flat-imaging,
science-imaging,...) following the requirements described in the file 
`filabes/instrument/configuration.yaml`.

### Compute combined bias images
```
$ filabres -n 17????_t2_CAFOS -rs bias
```

### Compute combined flat-imaging images
```
$ filabres -n 17????_t2_CAFOS -rs flat-imaging
```

### Reduce the science images
```
$ filabres -n 17????_t2_CAFOS -rs science-imaging
```
