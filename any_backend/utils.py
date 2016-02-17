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