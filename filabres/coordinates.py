import re


def obtain_coordinates_2(lista, idx):
    x1, x2, y1, y2 = lista[idx, :]
    return x1, x2, y1, y2


def obtain_coordinates_ccd(str_ccdsec):
    """Return x1, x2, y1, y2 from CCDSEC"""

    # replace colon by comma, and split by comma
    dumlist = re.sub(':', ',', str_ccdsec[1:-1]).split(',')

    # convert to integers
    x1, y1, x2, y2 = (int(i) for i in dumlist)
    return x1, x2, y1, y2
