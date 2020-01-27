import os
import csv
from astropy.io import fits
import numpy as np
from .salida_limpia import stdrobust, mostrarresultados
from .auxiliary_functions import save_file_csv


def create_list_cal_and_sci(lista_nights_, dir_lists_, dir_data_, desc_bias,
                            desc_flats, desc_arc, verbose, calysci):
    i = 0
    for night in lista_nights_:
        print('\n--> Working with night {}'.format(night))
        i += 1
        if night not in os.listdir(dir_lists_):
            newdir = dir_lists_ + night + '/'
            if verbose:
                print('Creating subdirectory {}'.format(newdir))
            os.mkdir(newdir)

            path_ = dir_data_ + night + '/'
            l_bias, l_flat, l_arc, l_ciencia, l_archivos, l_falla = \
                file_list_2(path_, desc_bias, desc_flats, desc_arc,
                            verbose, calysci)

            print('\n Summary of images/night')
            mostrarresultados(
                ['Bias', 'Flat', 'Arc', 'Science', 'Fault'],
                [len(l_bias), len(l_flat), len(l_arc), len(l_ciencia),
                 len(l_falla)],
                titulo=night, contador=i, valor_max=len(lista_nights_)
            )

            # store information in CSV files
            if verbose:
                print('\n--> Generating CSV files with image classification')
            for csvfile, l_object in zip(['science', 'allfiles', 'bias',
                                          'flat',
                                          'arc', 'fault'],
                                         [l_ciencia, l_archivos, l_bias,
                                          l_flat, l_arc, l_falla]):
                filename = dir_lists_ + night + '/' + csvfile + '.csv'
                # sort alphabetically before saving
                l_object.sort()
                save_file_csv(filename, l_object)
                if verbose:
                    print('File {} saved'.format(filename))
            if verbose:
                input('Press RETURN to continue...')


def create_unique_list(dir_data, night, stuff_list, keyword, binning=False,
                       filter_name=False):
    """Analysis and classification of useful region in all the images

    Parameters
    ----------
    dir_data : str
        Path to raw data.
    night : str
        Label identifying the observing night.
    stuff_list: list of strings
        List of filenames.
    keyword : str
        Keyword identifying the image region (e.g. CCDSEC).
    binning : bool
        If True, check for binning.
    filter_name : bool
        If True, check for filter_name.

    Returns
    -------
    lista: list of strings
        List of useful image regions (one item for each image).
        Typically, the geometry of the regions is repeated.
    unique_list: list of strings
        List with unique useful image regions.
    count_list: list of integers
        Number of images with each unique useful image region.
    indx_stuff: list of intergers
        List of integers (one for each image) indicating the
        unique useful image region.
    bin_sections: list
        List of pairs of numbers, indicating the binning for each
        image.
    name_filter: str
        Filter name.

    """

    lista = []
    for image in stuff_list:
        lista.append(
            fits.open(dir_data + night + '/' + image)[0].header[keyword]
        )
    # Counting each list
    unique_list, count_list = np.unique(lista, return_counts=True)

    bin_sections = -1 * np.ones((len(unique_list), 2), dtype=int)
    indx_stuff = np.zeros(len(stuff_list), dtype=int)
    name_filter = []

    for i in range(len(stuff_list)):
        for j in range(len(unique_list)):
            if lista[i] == unique_list[j]:
                indx_stuff[i] = j
                if binning:
                    bin_sections[j, 0] = \
                        int(fits.open(dir_data + night + '/' +
                                      stuff_list[i])[0].header['CCDBINX'])
                    bin_sections[j, 1] = \
                        int(fits.open(dir_data + night + '/' +
                                      stuff_list[i])[0].header['CCDBINY'])
                if filter_name:
                    name_filter.append(
                        fits.open(dir_data + night + '/' +
                                  stuff_list[i])[0].header['INSFLNAM'])
                break

    return (lista, unique_list, count_list, indx_stuff, bin_sections,
            name_filter)


def file_list_2(path_, desc_bias, desc_flats, desc_arc,
                verbose=False, calysci=True):
    lista_bias = []
    lista_flat = []
    lista_arc = []
    lista_science = []
    lista_files = []
    lista_wrong = []
    # No se usan como output REVISAR
    lista_cal = []
    lista_sci = []
    lista_misc = []
    lista_else = []

    # Listing every file in the folder
    for file in os.listdir(path_):
        if file.endswith(".fits"):
            if calysci:
                if '-cal-' in file:
                    lista_cal.append(file)
                elif '-sci-' in file:
                    lista_sci.append(file)
                else:
                    lista_misc.append(file)
            lista_files.append(os.path.join(path_, file))

            # Splitting by IMAGETYP
            header = fits.open(path_ + file)[0].header
            imagetyp = header['IMAGETYP'].lower()
            objectname_ = header['OBJECT']
            objectname = objectname_.lower()

            # Check it's not a test file
            if not fits.open(path_ + file)[0].header['OBJECT'] == 'Test':
                if imagetyp == 'bias':
                    found =  imagetyp in objectname
                    if found:
                        lista_bias.append(file)
                    else:
                        lista_wrong.append(file)
                    if verbose:
                        print(file, objectname, '<' + imagetyp + '>', found)
                elif imagetyp == 'flat':
                    found =  imagetyp in objectname
                    if found:
                        lista_flat.append(file)
                    else:
                        lista_wrong.append(file)
                    if verbose:
                        print(file, objectname, '<' + imagetyp + '>', found)
                elif imagetyp == 'arc':
                    found =  imagetyp in objectname
                    if found:
                        lista_arc.append(file)
                    else:
                        lista_wrong.append(file)
                    if verbose:
                        print(file, objectname, '<' + imagetyp + '>', found)
                elif imagetyp == 'science':
                    found = False
                    for text in ['bias', 'flat', 'arc']:
                        if text in objectname:
                            found = True
                    found = not found
                    if found:
                        lista_science.append(file)
                    else:
                        lista_wrong.append(file)
                    if verbose:
                        print(file, objectname, '<' + imagetyp + '>', found)
                else:
                    lista_else.append(file)

    for file in lista_wrong:

        if calysci:
            if file in lista_sci:
                lista_science.append(file)

        probable = most_probable_image(path_ + file)

        if probable == 0:
            lista_bias.append(file)
        elif probable == 1:
            lista_arc.append(file)
        elif probable == 2:
            lista_flat.append(file)

    return (lista_bias,
            lista_flat,
            lista_arc,
            lista_science,
            lista_files,
            lista_wrong)


def most_probable_image(archivo):
    image_data = fits.getdata(archivo, ext=0)
    v_median = np.median(image_data)
    v_sd = stdrobust(image_data)
    if v_sd < 50 and v_median < 900:
        probable = 0  # Bias
    elif v_sd < 500:
        probable = 1  # Arc
    else:
        probable = 2  # Flat

    return probable


def obtain_files_lists(path_):
    file_list = []
    for file in os.listdir(path_):
        if file.endswith(".fits"):
            file_list.append(os.path.join(path_, file))
    return file_list


def read_list(archivo):
    with open(archivo, 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        your_list = list(reader)
    your_list = [item for sublist in your_list for item in sublist]
    return your_list
