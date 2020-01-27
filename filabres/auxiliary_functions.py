import csv


def add_to_file(file, what):
    open(file, 'a+').write(what)


def obt_naxis(x2, x1, binn):
    naxis = int((x2 - x1 + 1) / binn)
    if (x2 - x1 + 1) % binn != 0:
        naxis += 1
    return naxis


def obtain_naxis(coordenadas_tupla, binn_1, binn_2):
    x1, x2, y1, y2 = coordenadas_tupla
    naxis1 = obt_naxis(x2, x1, binn_1)
    naxis2 = obt_naxis(y2, y1, binn_2)
    return naxis1, naxis2


def save_file_csv(csvfile, res):
    with open(csvfile, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for val in res:
            writer.writerow([val])


def slicing_data(slicing_push, size_da, size_mb):
    if slicing_push == "NW":
        s1 = size_da[0] - size_mb[0]
        s2 = size_da[0]
        s3 = 0
        s4 = size_mb[1]
    elif slicing_push == "SE":
        s1 = 0
        s2 = size_mb[0]
        s3 = size_da[1] - size_mb[1]
        s4 = size_da[1]
    elif slicing_push == "NE":
        s1 = size_da[0] - size_mb[0]
        s2 = size_da[0]
        s3 = 0
        s4 = size_mb[1]
    else:
        s1 = 0
        s2 = size_mb[0]
        s3 = 0
        s4 = size_mb[1]
    return s1, s2, s3, s4
