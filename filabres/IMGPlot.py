import argparse
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

from .salida_limpia import mostrarresultados, stdrobust


def coordenadas(x1, x2, y1, y2, args=None, hdr=None):
    if args:
        if args.imagesection is None and args.ccdsection is None:
            x1 = 1
            x2 = hdr['NAXIS1']
            y1 = 1
            y2 = hdr['NAXIS1']
        elif args.ccdsection:
            c_coordendas = sacar_coordenadas_ccd(hdr['DATASEC'])
            x1 = x1 - c_coordendas[0]
            x2 = x2 - c_coordendas[1]
            y1 = y1 - c_coordendas[2]
            y2 = y2 - c_coordendas[3]
    coordenadas_dibujo = (x1, x2, y1, y2)
    min_max_coorden = limites_imagen(*coordenadas_dibujo)

    return coordenadas_dibujo, min_max_coorden


def deshacer_tupla(tupla):
    if len(tupla) == 2:
        return tupla[0], tupla[1]
    if len(tupla) == 4:
        return tupla[0], tupla[1], tupla[2], tupla[3]


def escala(image2d, modo='cuantil'):
    if modo == 'cuantil':
        background = np.percentile(image2d, 10)
        foreground = np.percentile(image2d, 90)
        back_fore = (background, foreground)
    else:
        back_fore = (np.min(image2d), np.max(image2d))
    return back_fore


def imgdibujar(image2d, x1=None, x2=None, y1=None, y2=None,
               xmin=None, xmax=None, ymin=None, ymax=None,
               cmap='hot',
               background=None, foreground=None, verbose_=0):
    if not x1 and not x2 and not y1 and not y2 and not xmin and not xmax and not ymin and not ymax:
        x1 = 1
        y1 = 1
        x2 = image2d.shape[1]
        y2 = image2d.shape[0]
        limites = limites_imagen(x1, x2, y1, y2)
        xmin, xmax, ymin, ymax = deshacer_tupla(limites)

    if not background:
        background = np.percentile(image2d, 10)
    if not foreground:
        foreground = np.percentile(image2d, 90)

    if verbose_ == 1:
        print(image2d[(y1 - 1):y2, (x1 - 1):x2])
        print(image2d[(y1 - 1):y2, (x1 - 1):x2].shape)
        mostrarresultados(['x1', 'x2', 'y1', 'y2', -1,
                           'xmin', 'xmax', 'ymin', 'ymax', -1,
                           'background', 'foreground', -1,
                           'Mediana', 'Media', 'Std', 'relacion Y/X'],
                          [x1, x2, y1, y2, -1,
                           xmin, xmax, ymin, ymax, -1,
                           background, foreground, -1,
                           np.median(image2d), np.mean(image2d), stdrobust(image2d, 2),
                           round((xmax - xmin) / (ymax - ymin), 2)],
                          titulo='Parametros Imagen')

    # Se puede ir ampliando a medida que tenga mas funciones
    plt.figure()
    plt.imshow(image2d[(y1 - 1):y2, (x1 - 1):x2], cmap=cmap, aspect='auto',
               vmin=background, vmax=foreground,
               interpolation='nearest',
               origin='low',
               extent=[xmin, xmax, ymin, ymax])
    plt.colorbar()
    plt.show()


def limites_imagen(x1, x2, y1, y2):
    xmin = float(x1) - 0.5
    xmax = float(x2) + 0.5
    ymin = float(y1) - 0.5
    ymax = float(y2) + 0.5
    tupla_salida = (xmin, xmax, ymin, ymax)
    return tupla_salida


def sacar_coordenadas_ccd(imagen_, mypath_=None):
    if mypath_:
        strccdsec = fits.open(mypath_ + imagen_)[0].header['CCDSEC']
        longitud = len(strccdsec)
    else:
        strccdsec = imagen_
        longitud = len(strccdsec) + 1
    for x in range(1, longitud):
        if strccdsec[x] == ',':
            coma = x
            break
    for x in range(coma + 1, longitud):
        if strccdsec[x] == ':':
            puntos = x
            break
    for x in range(puntos + 1, longitud):
        if strccdsec[x] == ',':
            coma2 = x
            break

    x1 = int(strccdsec[1:coma])
    y1 = int(strccdsec[coma + 1: puntos])
    x2 = int(strccdsec[puntos + 1: coma2])
    y2 = int(strccdsec[coma2 + 1: -1])
    coordenadas_ccd = (x1, x2, y1, y2)
    return coordenadas_ccd


def main():
    parser = argparse.ArgumentParser(description="Draw the .fits image")
    group = parser.add_mutually_exclusive_group()
    group2 = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("file_name", type=str, help="File Name of the image")
    group2.add_argument("--imagesection", help="Section of IMAGE to be drawn. Input: [x1,y1:x2,y2]",
                        default=None)  # SistImg
    group2.add_argument("--ccdsection", help="Section of CCD to be drawn. Input: [x1,y1:x2,y2]",
                        default=None)  # SistFile
    parser.add_argument('--cmap', type=str, help="Colormap", default='hot')
    args = parser.parse_args()

    if args.imagesection:
        coordenadas_a_dibujar = sacar_coordenadas_ccd(args.imagesection)
    elif args.ccdsection:
        coordenadas_a_dibujar = sacar_coordenadas_ccd(args.ccdsection)
    else:
        coordenadas_a_dibujar = sacar_coordenadas_ccd(fits.open(args.file_name)[0].header['CCDSEC'])

    image_main = fits.open(args.file_name)
    hdr = image_main[0].header
    image2d = fits.getdata(args.file_name, ext=0)

    if not args.quiet:
        if args.verbose:
            resultverbose = ['File name', 'Verbose', 'Quiet', 'imagesection', 'ccdsection', -1]
            resuldverbose = [args.file_name, args.verbose, args.quiet, args.imagesection, args.ccdsection, -1]
        else:
            resultverbose = []
            resuldverbose = []

        mostrarresultados(resultverbose + ['NAXIS1', 'NAXIS2', -1,
                                           'Mediana', 'Std'],
                          resuldverbose + [hdr['NAXIS1'], hdr['NAXIS2'], -1,
                                           np.median(image2d), stdrobust(image2d, 2)],
                          titulo='Parametros')

    coordenadas_dibujo, limite_coordenadas = coordenadas(*coordenadas_a_dibujar, args, hdr)
    back_fore = escala(image2d, 'cuantil')

    imgdibujar(image2d,
               *coordenadas_dibujo,
               *limite_coordenadas,
               args.cmap,
               *back_fore)


if __name__ == "__main__":
    main()
