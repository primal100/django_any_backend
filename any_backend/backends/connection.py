from django.db.backends.base.base import BaseDatabaseWrapper
from operations import DatabaseOperations
from importlib import import_module

class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'easy_manager'
    compiler_module = 'compiler'

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        operations_cache = import_module(self.compiler_module)
        self.ops = DatabaseOperations(self, cache=operations_cache)
        self.client = self.client_initialization()

    def client_initialization(self):
        return None

