from django.db.backends.base.base import BaseDatabaseWrapper
from operations import DatabaseOperations
from importlib import import_module
from any_backend.utils import get_compiler_by_db_name
from cursor import Cursor

class DatabaseWrapper(BaseDatabaseWrapper):
    is_non_db = True
    vendor = 'nondb_backends'

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        compiler_module = get_compiler_by_db_name(args[0])
        client = None
        self._cache = import_module(compiler_module)
        self.ops = DatabaseOperations(self, cache=self._cache)

    def create_cursor(self):
        return Cursor

    def get_connection_params(self):
        if self._cache is None:
            raise ImportError('Connection class was not imported. Make sure a valid connection module string is set in your DatabaseWrapper')
        connection = getattr(self._cache, 'Connection')
        params = {'connection': connection}
        return params

    def get_new_connection(self, conn_params):
        connection_class = conn_params['connection']
        connection = connection_class(cursor = self.create_cursor())
        connection.setup()
        return connection

    def is_usable(self):
        return self.connection.check()

    def init_connection_state(self):
        pass


