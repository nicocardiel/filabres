from astropy.io import fits
from astropy.time import Time
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from .auxiliary_functions import obtain_naxis
from .coordinates import obtain_coordinates_ccd
from .dictionary import read_dictionary
from .generate_lists import read_list, create_unique_list
from .IMGPlot import imgdibujar
from .json_functions import load_json
from .mask_generation import create_circular_mask
from .salida_limpia import mostrarresultados
from .str2datetime import str2datetime


def decidir_repetir_calculos(norealizar, sirealizar, sujeto, dir_sujetos):
    existe_sujeto = os.path.exists('./df_' + sujeto + '.csv')
    lista_existentes = os.listdir(dir_sujetos)
    if not any([norealizar, sirealizar]):
        if existe_sujeto:
            print('Existe ya un dataframe de los ' + sujeto + '.')
            importado = pd.read_csv('./df_' + sujeto + '.csv')
            print(importado)
            input('importado')
            lista_teorica = importado.nombre_archivo.values.tolist()

            contador_t = 0
            contador_e = 0
            for i in range(len(lista_existentes)):
                if lista_teorica[i] in lista_existentes:
                    contador_t += 1
                if lista_existentes[i] in lista_teorica:
                    contador_e += 1

            if contador_e == len(lista_existentes) and \
                    contador_t == len(lista_teorica):
                print('Estan todos contabilizados, no hace falta recalcular '
                      'el dataframe de ' + sujeto + '.')
                realizar = False
            else:
                print('No estan todos los ' + sujeto + '. --> CALCULAR')
                realizar = True
        else:
            print('No existe el dataframe de ' + sujeto + '. --> CALCULAR')
            realizar = True
    elif norealizar:
        if existe_sujeto:
            print('Existe un dataframe de ' + sujeto + '. Se pide no repetir.')
            realizar = False
        else:
            print('No existe ningún dataframe de ' + sujeto + '. --> CALCULAR')
            realizar = True
    elif sirealizar:
        if existe_sujeto:
            print('Existe un dataframe de ' + sujeto +
                  ', pero se fuerza a calcularlo de nuevo.')
            realizar = True
        else:
            print('No existe el dataframe de ' + sujeto + '. --> CALCULAR')
            realizar = True
    else:
        raise ValueError('No cuadran las condiciones para los ' + sujeto + '!')

    return realizar


def reducing_images(list_nights, dir_listas, dir_datos, dir_bias,
                    dir_flats, dir_reduced,
                    df_bias, df_flat,
                    verbose=False, verbose_imagen=False):
    # Load lists
    element_list = None
    dic_filter = load_json()
    doesnt_exist_list = []
    total_science_images = 0
    saved_images = 0

    for night in list_nights:
        images_reduced_night = 0
        print(night)
        if night not in os.listdir(dir_reduced):
            os.mkdir(dir_reduced + night + '/')

        list_science = read_list(dir_listas + night + '/' + 'science.csv')
        doesnt_exist = (0, 0, len(list_science))

        secc, secc_unicas, secc_count, indice_secc, bin_secc, nombres_filtros = \
            create_unique_list(
                dir_datos, night, list_science, keyword='CCDSEC',
                binning=True, filter_name=True
            )
        i_image = 0
        for image in range(len(list_science)):
            i_image += 1
            # Image name
            name_science = dir_datos + night + '/' + list_science[image]
            header = fits.open(name_science)[0].header

            # Coordinates and binning
            coordinates = \
                obtain_coordinates_ccd(secc_unicas[indice_secc[image]])
            x1, x2, y1, y2 = coordinates
            binning = bin_secc[indice_secc[image]]
            naxis1_r = header['Naxis1']
            naxis2_r = header['Naxis2']

            naxis1_science, naxis2_science = \
                obtain_naxis((x1, x2, y1, y2), binning[0], binning[1])

            # Check for overscan
            biassec = header['BIASSEC']
            coordinates_biassec = obtain_coordinates_ccd(biassec)
            naxis1_overscan, naxis2_overscan = \
                obtain_naxis(coordinates_biassec, binning[0], binning[1])

            if coordinates_biassec[0] == 0 and coordinates_biassec[1] == 0:
                overscan = False
                x_1, x_2, y_1, y_2 = None, None, None, None
            else:
                print('There is overscan!')
                overscan = True

                # There is a need to cut the image. We generate the new
                # section for the image
                if coordinates_biassec[0] > x2:
                    x_1 = 0
                    x_2 = naxis2_science
                    y_1 = 0
                    y_2 = naxis1_science
                elif coordinates_biassec[3] > y2:
                    x_1 = 0
                    x_2 = naxis2_science
                    y_1 = 0
                    y_2 = naxis1_science
                elif coordinates_biassec[1] < x1:
                    x_1 = naxis2_overscan + 1
                    x_2 = naxis2_science + naxis2_overscan
                    y_1 = 0
                    y_2 = naxis1_science
                elif coordinates_biassec[4] < y1:
                    x_1 = 0
                    x_2 = naxis2_science
                    y_1 = naxis1_overscan + 1
                    y_2 = naxis1_science + naxis2_overscan
                else:
                    raise ValueError('Where is the overscan?!')

            # We obtain the name of the filter and it's ID_filter
            filtername = nombres_filtros[image]
            id_filter = read_dictionary(filtername, dic_filter)

            # Julian Date
            isot_time = header['DATE']
            date_datetime = str2datetime(isot_time)
            time_isot = Time(isot_time, format='isot', scale='utc')

            if verbose:
                mostrarresultados(
                    ['noche', 'naxis1_r', 'naxis2_r', 'naxis1_c', 'naxis2_c',
                     'x1', 'x2', 'y1', 'y2',
                     'binning', 'filtro', 'id_filtro',
                     'FJM', 'Overscan',
                     'imagen', 'nombre',
                     'fecha', 'hora'],
                    [night, naxis1_r, naxis2_r, naxis1_science, naxis2_science,
                     x1, x2, y1, y2,
                     binning, filtername, id_filter,
                     time_isot.jd, overscan,
                     image, list_science[image],
                     date_datetime.date(), date_datetime.time()],
                    contador=i_image, valor_max=len(list_science))

            # Buscamos el Bias
            # Seleccionamos los que coinciden con el tamaño teorico
            datat = df_bias[df_bias.Naxis1 == naxis1_science]
            datat = datat[datat.Naxis2 == naxis2_science]
            datat = datat[datat.Binning1 == binning[0]]
            datat = datat[datat.Binning2 == binning[1]]
            fechasjd_b = abs(datat.julian.values - time_isot.jd)
            if len(fechasjd_b) > 0:
                pos_min = np.argmin(fechasjd_b)
                nombre_bias_buscado = datat.iloc[pos_min]['nombre_archivo']
                if datat.iloc[pos_min]['noche'] != night:
                    if verbose:
                        print('El bias mas cercano no es de esta noche.')

                bias_asociado = fits.getdata(
                    dir_bias + nombre_bias_buscado, ext=0)
            else:
                nombre_bias_buscado = 'Ausente'
                relleno_b = 680
                if verbose:
                    print('No se han encontrado bias de esa forma, '
                          'se genera uno artificial.')
                bias_asociado = np.full((naxis1_science, naxis2_science),
                                        relleno_b, dtype=float)

            # Buscamos el Flat
            # Seleccionamos los que coinciden con el tamaño teorico
            dataf = df_flat[df_flat.Naxis1 == naxis1_science]
            dataf = dataf[dataf.Naxis2 == naxis2_science]
            dataf = dataf[dataf.Binning1 == binning[0]]
            dataf = dataf[dataf.Binning2 == binning[1]]
            dataf = dataf[dataf.filtro == id_filter]

            # Lista de los bias en función de la distancia en tiempo a la
            # imagen de ciencia
            fechasjd_f = abs(dataf.julian.values - time_isot.jd)
            if len(fechasjd_f) > 0:
                pos_min = np.argmin(fechasjd_f)
                nombre_flat_buscado = dataf.iloc[pos_min]['nombre_archivo']
                if dataf.iloc[pos_min]['noche'] != night:
                    if verbose:
                        print('Existe un Flat, pero no es de esta noche.')
                flat_asociado = fits.getdata(dir_flats + nombre_flat_buscado,
                                             ext=0)

            else:
                nombre_flat_buscado = 'Ausente'
                relleno_f = 1
                print('No se han encontrado flats, '
                      'se genera uno artificialmente.')
                flat_asociado = np.full((naxis1_science, naxis2_science),
                                        relleno_f, dtype=float)

            # Obtenemos la información de la imagen de ciencia
            image_data = fits.getdata(name_science, ext=0)
            reducido_header = header.copy()

            # Comprobamos si hay o no overscan que haya que tener en cuenta
            if overscan:
                print('Recortamos los datos')
                image_data = image_data[y_1:y_2, x_1:x_2]

            ###################################################################
            reducido_datos = (image_data - bias_asociado) / flat_asociado
            ###################################################################

            if verbose_imagen:
                imgdibujar(reducido_datos)
                plt.show()

            if reducido_header['BLANK']:
                del reducido_header['BLANK']

            # Sacar si tiene o no un grisma
            numero_grisma = reducido_header['insgrid'].replace(' ', '0')[6:8]
            # Si numero_grisma==11, entonces no hay grisma de por medio
            if numero_grisma == 11:
                free_grisma = True
            else:
                free_grisma = False

            if free_grisma:
                # se puede cambiar el centro y el radio
                mask = create_circular_mask(naxis1_science, naxis2_science)
                reducido_datos[~mask] = 1

            ahora = datetime.datetime.now()
            ahora_dt = Time(ahora, format='datetime', scale='utc')
            reducido_header.add_history(
                'Realizada la reduccion a partir de estas imagenes: | ' +
                str(ahora_dt)[:19]
            )
            reducido_header.add_history('Bias: ' + nombre_bias_buscado)
            reducido_header.add_history('Flat: ' + nombre_flat_buscado)

            # Guardamos la imagen
            reducido_final = fits.PrimaryHDU(
                reducido_datos.astype(np.float32), reducido_header
            )

            reducido_final.writeto(dir_reduced + night + '/' + 'r_' +
                                   list_science[image], overwrite=True)

            images_reduced_night += 1

            ahora = datetime.datetime.now()
            time_isot = Time(ahora, format='datetime', scale='utc')
            if element_list is None:
                element_list = pd.DataFrame(
                    [[naxis1_science, naxis2_science,
                      x1, x2, y1, y2,
                      binning[0], binning[1],
                      id_filter,
                      free_grisma, numero_grisma,
                      'r_' + list_science[image],
                      nombre_bias_buscado, nombre_flat_buscado,
                      night, time_isot, time_isot.jd]],
                    columns=['Naxis1', 'Naxis2',
                             'x1', 'x2', 'y1', 'y2',
                             'Binning1', 'Binning2',
                             'filtro',
                             'free_grisma', 'num_grisma',
                             'nombre_archivo',
                             'nombre bias', 'nombre flat',
                             'noche', 'Fecha realizacion', 'julian']
                )
            else:
                elemento_lista_ = pd.DataFrame(
                    [[naxis1_science, naxis2_science,
                      x1, x2, y1, y2,
                      binning[0], binning[1],
                      id_filter,
                      free_grisma, numero_grisma,
                      'r_' + list_science[image],
                      nombre_bias_buscado, nombre_flat_buscado,
                      night, time_isot, time_isot.jd]],
                    columns=['Naxis1', 'Naxis2',
                             'x1', 'x2', 'y1', 'y2',
                             'Binning1', 'Binning2',
                             'filtro',
                             'free_grisma', 'num_grisma',
                             'nombre_archivo',
                             'nombre bias', 'nombre flat',
                             'noche', 'Fecha realizacion', 'julian']
                )
                element_list = pd.concat([element_list, elemento_lista_],
                                         ignore_index=True)

        # Al final de cada noche se hace el recuento
        doesnt_exist_list.append(doesnt_exist)
        saved_images += images_reduced_night
        if verbose:
            mostrarresultados(['Imagenes reducidas', 'Acumulado'],
                              [images_reduced_night, saved_images],
                              titulo="Reduccion de Imagenes",
                              contador=list_nights.index(night),
                              valor_max=len(list_nights))
            input("Press RETURN to continue...")

    mostrarresultados(list_nights, doesnt_exist_list)
    no_existen_2 = [0, 0]
    _ = element_list.to_csv('df_reduced.csv', index=None, header=True)
    for i in range(len(doesnt_exist_list)):
        total_science_images += doesnt_exist_list[i][2]
        no_existen_2[0] += doesnt_exist_list[i][0]
        no_existen_2[1] += doesnt_exist_list[i][1]

    print('Biases que no ha funcionado: ', no_existen_2[0],
          '| Flats que no ha funcionado: ', no_existen_2[1],
          '| Imagenes en total: ', total_science_images,
          '| Imagenes reducidas: ', saved_images)

    return saved_images
