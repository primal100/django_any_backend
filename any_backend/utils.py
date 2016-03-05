from django.conf import settings
from importlib import import_module
from django.contrib.contenttypes.models import ContentType

def get_db_by_name(name):
    db = settings.DATABASES[name]
    return db

def get_models_for_db(db_alias):
    models = []
    for type in ContentType.objects.all():
        model = type.model_class()
        if getattr(model, 'non_db', None) == db_alias:
            models.append(model)
    return models

def get_compiler_by_db_name(name):
    db = get_db_by_name(name)
    return db.get('COMPILER', None)

def get_wrapper_by_db_name(name):
    db = get_db_by_name(name)
    module = import_module(db['ENGINE'] + '.base')
    db_wrapper_class = getattr(module, 'DatabaseWrapper')
    return db_wrapper_class

def backend_is_non_db(name):
    db_wrapper_class = get_wrapper_by_db_name(name)
    is_non_db = getattr(db_wrapper_class, 'is_non_db', False)
    return is_non_db

def get_db_for_model(model):
    dbs = settings.DATABASES
    db_table = model._meta.db_table
    for k, v in dbs.iteritems():
        models = v.get('MODELS', [])
        if any(db_table.lower() == x.lower() for x in models):
            return k
    return None

def make_dict_from_obj(object):
    obj2dict = {}
    attrs = dir(object)
    for attr in attrs:
        if not attr.startswith('__'):
            obj2dict[attr] = getattr(object, attr, None)
    return obj2dict

def getvalue(object, attr, returnIfNone='raise'):
    value_set, value = False, ''
    attrs = [attr, attr.lower(), attr.capitalize(), attr.upper()]
    for i, has in enumerate([hasattr(object, x) for x in attrs]):
        if has:
            value = getattr(object, attrs[i])
            value_set = True
            break
    if value_set:
        return value
    keys = object.keys()
    for i, has in enumerate([x in keys for x in attrs]):
        if has:
            value = object[attrs[i]]
            value_set = True
            break
    if value_set:
        return value
    elif returnIfNone == 'raise':
       raise ValueError('Value for %s not found' % attr)
    return returnIfNone

def toDicts(obj_list):
    dictlist = []
    for object in obj_list:
        dictlist.append(make_dict_from_obj(object))
    return dictlist