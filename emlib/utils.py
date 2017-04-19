
from json import dumps

def get_properties(instance):
    return dumps(vars(instance))

