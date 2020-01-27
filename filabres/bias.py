from astropy.io import fits
from astropy.time import Time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

from .auxiliary_functions import obtain_naxis, slicing_data
from .coordinates import obtain_coordinates_2, obtain_coordinates_ccd
from .generate_lists import read_list, create_unique_list
from .IMGPlot import imgdibujar, limites_imagen
from .salida_limpia import mostrarresultados


def join_bias_images(night, unique_sections_, coordinates_sections_,
                     sections_count_, indx_section_,
                     bin_sections_, dir_bias_, dir_data_, list_bias_,
                     interactive=False, cut_extra=False,
                     verbose=False, verbose_imagen=False):
    """Combine multiple bias to generate a master bias.

    """

    list_element = None
    for section in range(len(unique_sections_)):
        if verbose:
            print('\nsection: ' + str(section))
        coordinates_image = \
            obtain_coordinates_2(coordinates_sections_, section)
        x1, x2, y1, y2 = coordinates_image

        # Obtain Binning
        ccdbinx = bin_sections_[section, 0]
        ccdbiny = bin_sections_[section, 1]

        naxis1_expected, naxis2_expected = \
            obtain_naxis(coordinates_image, ccdbinx, ccdbiny)

        master_bias = np.zeros(
            (sections_count_[section],
             naxis2_expected,
             naxis1_expected),
            dtype=float
        )

        index0 = 0
        slicing_push = False
        header = None
        for image in range(len(list_bias_)):
            if indx_section_[image] == section:
                image_file = dir_data_ + night + '/' + list_bias_[image]
                image_data = fits.getdata(image_file, ext=0)
                if image_data[:, :].shape == master_bias[index0, :, :].shape:
                    master_bias[index0, :, :] = image_data[:, :]  # Juntar
                    if index0 == 0:
                        header = fits.open(image_file)[0].header
                else:
                    size_mb = master_bias[index0, :, :].shape
                    size_da = image_data[:, :].shape
                    if cut_extra:
                        if not slicing_push:
                            warnings.warn("Sizes Incompatible!")
                            print("Sizes incompatible:")
                            print("Data size: " + str(size_da))
                            print("Master Bias size: " + str(size_mb) + "\n")
                            slicing_push = (input(
                                "Slicing fits. Select side towards to push "
                                "(SW), SE, NE, NW: ") or "SW")
                        s1, s2, s3, s4 = slicing_data(
                            slicing_push, size_da, size_mb
                        )
                        master_bias[index0, :, :] = image_data[s1:s2, s3:s4]
                    else:
                        warnings.warn("Sizes Incompatible!")
                        print("Sizes incompatible:")
                        print("Data size: " + str(size_da))
                        print("Master Bias size: " + str(size_mb) + "\n")
                        print("Skipping current Master Bias.")
                        print("Consider using slicing with '--recortar'. ")
                        input("Press Enter to continue...")
                        break
                index0 += 1

        master_bias_colapsed = np.median(master_bias, axis=0)
        if verbose_imagen:
            imgdibujar(master_bias_colapsed, verbose_=1)
            plt.show()
        file_name = \
            night + \
            "-{:04d}_{:04d}_{:04d}_{:04d}".format(x1, x2, y1, y2) + \
            "-B{:02d}_{:02d}.fits".format(ccdbinx, ccdbiny)
        print('Output master bias will be {}'.format(file_name))
        if verbose:
            mostrarresultados(
                ['N', 'CCDBINX', 'CCDBINY', 'NAXIS1', 'NAXIS2', '-1'],
                [len(indx_section_[indx_section_ == section]),
                 ccdbinx, ccdbiny,
                 naxis1_expected, naxis2_expected, file_name],
                titulo='Bias Realizado'
            )

        if header is None:
            raise ValueError('No se ha creado correctamente la cabecera')

        masterbias_header = header.copy()

        ahora = datetime.datetime.now()
        ahora_dt = Time(ahora, format='datetime', scale='utc')
        masterbias_header.add_history(
            'Realizado Bias a partir de ' +
            str(len(
                indx_section_[indx_section_ == section])) + ' imagenes. | ' +
            str(ahora_dt)[:19])
        numero_bias = 0
        for bias_raw in range(len(list_bias_)):
            if indx_section_[bias_raw] == section:
                numero_bias += 1
                masterbias_header.add_history(
                    str(numero_bias) + ': ' + list_bias_[bias_raw])
                if verbose:
                    print('{:3d}: {}'.format(numero_bias,
                                             list_bias_[bias_raw]))

        # remove BLANK keyword (otherwise one gets the following warning:
        # "The 'BLANK' keyword is only applicable to integer data"
        if 'BLANK' in masterbias_header:
            del masterbias_header['BLANK']

        # save master bias
        masterbias_final = fits.PrimaryHDU(
            master_bias_colapsed.astype(np.float32), masterbias_header)
        masterbias_final.writeto(dir_bias_ + file_name, overwrite=True)

        if verbose_imagen:
            coord_lim = limites_imagen(*coordinates_image)
            imgdibujar(master_bias_colapsed, *coordinates_image, *coord_lim,
                       verbose_=1)

        if interactive:
            input("Press Enter to continue...")

        # Add to table
        isot_time = masterbias_header['DATE']
        time_ = Time(isot_time, format='isot', scale='utc')
        if list_element is None:
            list_element = pd.DataFrame(
                [[naxis1_expected, naxis2_expected,
                  x1, x2, y1, y2,
                  ccdbinx, ccdbiny,
                  file_name, night,
                  time_, time_.jd]],
                columns=['Naxis1', 'Naxis2',
                         'x1', 'x2', 'y1', 'y2',
                         'Binning1', 'Binning2',
                         'nombre_archivo', 'noche',
                         'tiempo_astropy', 'julian']
            )
        else:
            list_element_ = pd.DataFrame(
                [[naxis1_expected, naxis2_expected,
                  x1, x2, y1, y2,
                  ccdbinx, ccdbiny,
                  file_name, night,
                  time_, time_.jd]],
                columns=['Naxis1', 'Naxis2',
                         'x1', 'x2', 'y1', 'y2',
                         'Binning1', 'Binning2',
                         'nombre_archivo', 'noche',
                         'tiempo_astropy', 'julian']
            )
            list_element = pd.concat([list_element, list_element_],
                                     ignore_index=True)

    return list_element


def make_master_bias(list_nights, dir_lists, dir_data, dir_bias,
                     interactive, cut_reshape,
                     verbose=False, verbose_imagen=False):
    """Generate master bias

    """

    i_noche = 0
    df_bias = None
    for night in list_nights:
        i_noche += 1
        print('\n=== NIGHT ' + night + ' - (' + str(i_noche) + '/' +
              str(len(list_nights)) + ') ===')

        list_bias = read_list(dir_lists + night + '/' + 'bias.csv')

        # analysis and classification of useful region in all the images
        sections, unique_section, section_counting, \
            section_index, bin_sections, _ = create_unique_list(
                dir_data, night, list_bias, keyword='CCDSEC', binning=True
            )

        sections_coordinates = np.zeros((len(unique_section), 4), dtype=int)
        for i in range(len(unique_section)):
            unique_coordinates = obtain_coordinates_ccd(unique_section[i])
            sections_coordinates[i, :] = [*unique_coordinates]

        df_bias_ = join_bias_images(
            night, unique_section, sections_coordinates, section_counting,
            section_index, bin_sections, dir_bias, dir_data, list_bias,
            interactive=interactive, cut_extra=cut_reshape,
            verbose=verbose,
            verbose_imagen=verbose_imagen
        )
        if df_bias is None:
            df_bias = df_bias_
        else:
            df_bias = pd.concat([df_bias, df_bias_], ignore_index=True)

    return df_bias


def obtain_bias(dir_bias_, night, list_nights, list_bias,
                x1, x2, y1, y2, b1, b2,
                max_search=10, fill_bias=680, verbose=False):
    """
    Searches the list of available bias for a bias with the same night the
    photo was taken. Also checks size nd binning.
    If it finds such a bias, it will use that one directly.
    If it does not find one, it will look for a different bias which fits
    the desired parametres for other nights.
    If there aren't any, it generates a flat bias.

    :param dir_bias_:
    :param night:
    :param list_nights:
    :param list_bias:
    :param x1:
    :param x2:
    :param y1:
    :param y2:
    :param b1:
    :param b2:
    :param max_search:
    :param fill_bias:
    :param verbose:
    :return:
    """

    searched_bias_name = \
        dir_bias_ + night + \
        "-{0:04d}_{1:04d}_{2:04d}_{3:04d}-B{4:02d}_{5:02d}.fits".format(
            x1, x2, y1, y2, b1, b2)
    exist = None
    take_another = False
    if searched_bias_name in list_bias:
        exist = True
    else:
        position = list_nights.index(night)
        for i in range(1, max_search):
            for mult in [-1, 1]:
                indx = i * mult
                position_new = position + indx
                if position_new >= len(list_nights):
                    # Reached end of the year. Doesn't search for next year.
                    # Can be fixed with a bigger folder and
                    # placing every night in a same folder
                    break
                night = list_nights[position_new]
                searched_bias_new = \
                    dir_bias_ + night + \
                    "-{0:04d}_{1:04d}_{2:04d}_{3:04d}-B{4:02d}_{5:02d}.fits" \
                    .format(x1, x2, y1, y2, b1, b2)

                if searched_bias_new in list_bias:
                    searched_bias_name = searched_bias_new
                    exist = True
                    take_another = True

    if exist:
        if verbose:
            if take_another:
                print('Bias taken from another night. The taken bias is:')
                print(searched_bias_name)
            else:
                print('Bias exists.')
        searched_bias = fits.getdata(searched_bias_name, ext=0)
    else:
        if verbose:
            print('There are no nearby bias available. '
                  'A filled bias has been generated.')
        naxis1_expected, naxis2_expected = \
            obtain_naxis((x1, x2, y1, y2), b1, b2)

        searched_bias = np.full((naxis1_expected, naxis2_expected),
                                fill_bias, dtype=float)

    return exist, searched_bias_name, searched_bias
