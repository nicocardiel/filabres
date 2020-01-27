import json
import os

def load_json(filename='dic_filtro.json'):
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
    else:
        data = dict()
    return data


def save_json(variable, filename):
    json_f = json.dumps(variable, indent=2, sort_keys=True)
    f = open(filename, "w")
    f.write(json_f)
    f.close()
