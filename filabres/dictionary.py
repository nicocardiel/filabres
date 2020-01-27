from .json_functions import save_json


def read_dictionary(name, dictionary_, filename='dic_filtro.json'):
    """
    Busca en el diccionario el número del filtro buscado. Si no existe, crea uno nuevo

    :param name:
    :param dictionary_:
    :param filename:
    :return:
    """
    if name in dictionary_:
        return dictionary_[name]
    else:
        len_dic = len(dictionary_)
        dictionary_[name] = len_dic
        print('New dictionry entry: Filter {0} - Index {1:03d}'.format(name, dictionary_[name]))
        save_json(dictionary_, filename)
        return dictionary_[name]


def show_dictionary(dictionary_name):
    print("Showing dictionary: ")
    for x, y in dictionary_name.items():
        print(x, y)
