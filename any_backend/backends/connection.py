from django.db.backends.base.base import BaseDatabaseWrapper
from operations import DatabaseOperations
from importlib import import_module
from any_backend.utils import get_compiler_by_db_name
from any_backend.utils import get_db_by_name
from cursor import Cursor

class DatabaseWrapper(BaseDatabaseWrapper):
    is_non_db = True
    default_compiler = 'any_backend.backends.compiler'

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.db_name = args[0]
        self.db_config = get_db_by_name(self.db_name)
        compiler_module = get_compiler_by_db_name(self.db_name) or self.default_compiler
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
        connection = connection_class(self.create_cursor(), self.db_config)
        connection.setup()
        return connection

    def is_usable(self):
        return self.connection.check()

    def init_connection_state(self):
        pass


