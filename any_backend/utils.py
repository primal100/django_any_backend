from django.conf import settings
from importlib import import_module

def get_db_by_name(name):
    db = settings.DATABASES[name].engine
    return db

def get_compiler_by_db_name(name):
    db = get_db_by_name(name)
    return db['COMPILER']

def get_wrapper_by_db_name(name):
    db = get_db_by_name(name)
    module = import_module(db.connection)
    db_wrapper_class = getattr(module, 'DatabaseWrapper')
    return db_wrapper_class

def backend_is_non_db(name):
    db_wrapper_class = get_wrapper_by_db_name(name)
    is_db = getattr(db_wrapper_class, 'is_non_db', False)
    return not is_db

def model_is_non_db(model):
    meta = model._meta
    return getattr(meta, 'nodb_backend', None)

def make_dict_from_obj(object):
    obj2dict = {}
    attrs = dir(object)
    for attr in attrs:
        if not attr.startswith('__'):
            obj2dict[attr] = getattr(object, attr, None)
    return obj2dict

def convert_object(object, field_names):
    new_dict = {}
    object = getattr(object, '__dict__', object)
    for k,v in object.iteritems():
        if isinstance(v, dict):
            new_dict.update(convert_object(v, field_names))
        elif hasattr(v, '__dict__'):
            obj2dict = make_dict_from_obj(v)
            new_dict.update(convert_object(obj2dict, field_names))
        elif any(k in f for f in field_names):
            index = field_names.index(k)
            new_dict[index] = v
    return new_dict

def convert_to_tuples(objects, field_names):
    if objects:
        if type(object) == tuple:
            return objects
        elif type(object) == list:
            for index, obj in enumerate(objects):
                objects[index] = tuple(obj)
            return objects
        else:
            list_of_tuples = []
            for object in objects:
                new_tuple = tuple(convert_object(object, field_names).values())
                list_of_tuples.append(new_tuple)
            return list_of_tuples
    else:
        return []