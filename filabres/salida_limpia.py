import numpy as np


def meter0(x, n):
    x = str(x)
    while len(x) < n:
        x = '0' + x
    return x


def mostrarresultados(nombres, valores, contador=None, valor_max=None,
                      titulo='Resultados', relleno='.', separador='%'):
    tamanyo = []
    if contador:
        if valor_max:
            valor_max = str(valor_max)
            contador = meter0(contador, len(valor_max))
        else:
            contador = str(contador)
            if len(contador) % 2 == 1:
                contador = '0' + contador
    for i in range(len(nombres)):
        if str(nombres[i]) != '-1':
            tamanyo.append(len(str(nombres[i]))+len(str(valores[i])))

    if contador:
        if valor_max:
            tamanyom = max(max(tamanyo) + 5, len(titulo) + 8,
                           len(contador)*2 + 6, 24)
        else:
            tamanyom = max(max(tamanyo) + 5, len(titulo) + 8,
                           len(contador) + 6, 24)
    else:
        tamanyom = max(max(tamanyo) + 5, len(titulo) + 8, 24)

    if '-1' in nombres:
        for i in range(len(nombres)):
            if str(nombres[i]) == '-1':
                if not str(valores[i]) == '-1':
                    tamanyo.append(len(valores[i]))

        if not tamanyom == max(tamanyo):
            tamanyom = max(tamanyo)

    if len(titulo) % 2 != tamanyom % 2:
        tamanyom += 1
    decorres = rellenar('-', (tamanyom - len(titulo) - 2) / 2)
    titulo = decorres + ' ' + titulo + ' ' + decorres

    if contador:
        if valor_max:
            decocierre = rellenar('-', (tamanyom - len(contador)*2 - 3) / 2)
            cierre = decocierre + ' ' + contador + '/' + valor_max + ' ' + \
                     decocierre
        else:
            decocierre = rellenar('-', (tamanyom - len(contador) - 3) / 2)
            cierre = decocierre + ' ' + contador + ' ' + decocierre + '\n'
    else:
        cierre = rellenar('-', tamanyom)

    print(titulo)
    for nombre_, tamanyo_, valor_ in zip(nombres, tamanyo, valores):
        if all([str(nombre_) == '-1', str(valor_) == '-1']):
            print(rellenar(separador, tamanyom))

        elif all([str(nombre_) == '-1', str(valor_) != '-1']):
            print(str(valor_))
        else:
            print(nombre_ + ': ' +
                  rellenar(relleno, tamanyom - tamanyo_ - 3) +
                  ' ' + str(valor_))
    print(cierre)


def rellenar(x0, n):
    x = x0
    while len(x) < n:
        x = x + x0
    return x


def stdrobust(array, redondear=None):
    salida = 0.7413 * (np.quantile(array.reshape(-1,), 0.75) -
                       np.quantile(array.reshape(-1,), 0.25))
    if redondear:
        salida = np.round(salida, redondear)
    return salida
