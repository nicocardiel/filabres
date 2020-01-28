# -*- coding: utf-8 -*-

"""Basic data reduction of CAHA data.

Project started with the "Prácticas en Empresa" of Enrique Galcerán García
(Astrophysics Master, Universidad Complutense de Madrid, course 2018-2019).
See details in: https://github.com/enriquegalceran/PE-CAHA

The basic ideas from Galcerán's project have been used by Nicolás Cardiel to
implement filabres, trying to speed up the execution time and generalizing
the algorithms to be useful for additional instruments and observing modes.

This code is hosted at: https://github.com/nicocardiel/filabres

"""

import argparse
import os
import pandas as pd
import time
import yaml

from .load_instrument_configuration import load_instrument_configuration

from .bias import make_master_bias
from .flat import make_master_flat
from .generate_lists import obtain_files_lists, create_list_cal_and_sci
from .reduction import reducing_images, decidir_repetir_calculos
from .salida_limpia import mostrarresultados


def check_tslash(dumdir):
    """Auxiliary function to add trailing slash when not present"""
    if dumdir[-1] != '/':
        dumdir += '/'
    return dumdir


def main():

    # Default values (important: don't forget the trailing slash)
    dir_bias = 'bias/'
    dir_listas = 'lists/'
    dir_flats = 'flats/'
    dir_reduced = 'reduced/'
    required_subdirectories = [dir_bias, dir_flats, dir_listas, dir_reduced]

    # parse command-line options
    parser = argparse.ArgumentParser(
        description="Basic data reduction of CAHA data")
    # group1 = parser.add_mutually_exclusive_group()
    # group2 = parser.add_mutually_exclusive_group()

    parser.add_argument("-q", "--quiet", action="store_true",
                        help="run quietly (reduced verbosity)")
    parser.add_argument("-i", "--instrument", type=str,
                        help="instrument identification")
    parser.add_argument("-d", "--datadir", type=str,
                        help='data Directory')
    parser.add_argument("--step", type=str, help="reduction step")
    # parser.add_argument("-vi", "--verboseimage", action="store_true",
    #                     help="Mostrar Imagenes")
    # parser.add_argument("--recortar", action="store_true",
    #                     help="Activar el recorte de imagenes")
    # parser.add_argument("--calysci", action="store_false",
    #                     help="Usar cuando los archivos no tienen '-cal-' y "
    #                          "'-sci-' en el nombre para diferenciar entre "
    #                          "calibración y ciencia.")
    # parser.add_argument("-nr", "--noreducc", action="store_false",
    #                     help="No realizar la reduccion.")
    # group1.add_argument("-nb", "--nobias", action="store_true",
    #                     help="No realizar los Master Bias.")
    # group1.add_argument("-sb", "--sibias", action="store_true",
    #                     help="Fuerza realizar los Master Bias.")
    #
    # group2.add_argument("-nf", "--noflat", action="store_true",
    #                     help="No realizar los Master Flat.")
    # group2.add_argument("-sf", "--siflat", action="store_true",
    #                     help="Fuerza realizar los Master Flat.")

    args = parser.parse_args()

    # ---

    # set verbosity
    verbose = not args.quiet

    # import instrument configuration
    instconf = load_instrument_configuration(args.instrument)

    # ToDo: continue here

    # check required subdirectories
    for subdir in required_subdirectories:
        if os.path.isdir(subdir):
            if verbose:
                print('Subdirectory {} found'.format(subdir))
        else:
            print('Subdirectory {} not found. Creating it!'.format(subdir))
            os.makedirs(subdir)

    # add trailing slash in subdirectory names when not present
    datadir = check_tslash(args.datadir)
    if verbose:
        print('Data directory: {}'.format(datadir))

    # Comprobamos si queremos/hace falta calcular los bias
    if verbose:
        print('* BIAS:', args.nobias, args.sibias)
    realizarbias = decidir_repetir_calculos(
        args.nobias, args.sibias, 'bias', dir_bias
    )

    # Comprobamos si queremos/hace falta calcular los flats
    if verbose:
        print('* FLATS:', args.noflat, args.siflat)
    realizarflat = decidir_repetir_calculos(
        args.noflat, args.siflat, 'flat', dir_flats
    )

    # Creamos una lista de las noches disponibles
    lista_noches = os.listdir(datadir)
    lista_noches.sort()
    if verbose:
        print('Total number of nights found:', len(lista_noches))
        for night in lista_noches:
            print(night)

    # set execution time
    tiempo_inicio = time.time()

    # Separamos entre calibración y ciencia
    if verbose:
        input('Press RETURN to continue...')
    print('\n'
          '*** Classifying images within each night ***')
    print('============================================')
    create_list_cal_and_sci(lista_noches, dir_listas, datadir,
                            verbose, args.calysci)
    tiempo_listas = time.time()

    # Creamos los Master Biases
    print('\n*** Handling master bias images ***')
    print('===================================')
    if realizarbias:
        df_bias = make_master_bias(
            lista_noches,  dir_listas, datadir, dir_bias,
            args.recortar,
            verbose=verbose, verbose_imagen=args.verboseimage
        )
        numero_bias = len(os.listdir(dir_bias))
        print('\n--> Generating df_bias.csv...')
        print(df_bias)
        _ = df_bias.to_csv('df_bias.csv', index=None, header=True)
    else:
        print('--> Importing df_bias.csv...')
        df_bias = pd.read_csv('df_bias.csv')
        numero_bias = '-'

    lista_bias = obtain_files_lists(dir_bias)
    tiempo_biases = time.time()
    if verbose:
        input('Press RETURN to continue...')

    # Creamos los Master Flats
    print('\n*** Handling master flat images ***')
    print('===================================')
    if realizarflat:
        df_flat = make_master_flat(
            lista_noches, lista_bias,
            dir_listas, datadir, dir_bias, dir_flats,
            verbose=verbose, verbose_imagen=args.verboseimage
        )
        numero_flats = len(os.listdir(dir_flats))
        print('\n--> Generating df_flat.csv...')
        print(df_flat)
        _ = df_flat.to_csv('df_flat.csv', index=None, header=True)
    else:
        print('--> Importing df_flat.csv...')
        df_flat = pd.read_csv('df_flat.csv')
        numero_flats = '-'

    tiempo_flats = time.time()
    if verbose:
        input('Press RETURN to continue...')

    # Juntamos todos los procesos y relizamos la reducción
    print('\n*** Handling scientific images ***')
    print('==================================')
    if args.noreducc:
        numeros_reducidos = reducing_images(
            lista_noches, dir_listas, datadir, dir_bias, dir_flats,
            dir_reduced, df_bias, df_flat,
            verbose, verbose_imagen=args.verboseimage)
    else:
        numeros_reducidos = '-'
    tiempo_reducc = time.time()

    # Mostramos resultados de ambos procesos
    mostrarresultados(
        ['Tiempo Listas', 'Tiempo Master Bias', 'Tiempo Master Flats',
         'Tiempo Reduccion', 'Tiempo Total', 'Cuantos Biases', 'Cuantos Flats',
         'Cuantos Reducidos'],
        [round(tiempo_listas - tiempo_inicio, 2),
         round(tiempo_biases - tiempo_listas, 2),
         round(tiempo_flats - tiempo_biases, 2),
         round(tiempo_reducc - tiempo_flats, 2),
         round(tiempo_reducc - tiempo_listas, 2),
         numero_bias, numero_flats, numeros_reducidos],
        titulo='Tiempo Ejecucion')


if __name__ == "__main__":

    main()
