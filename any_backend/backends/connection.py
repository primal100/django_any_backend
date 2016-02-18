from django.db.backends.base.base import BaseDatabaseWrapper
from operations import DatabaseOperations
from importlib import import_module
from any_backend.utils import get_compiler_by_db_name

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

class Cursor(object):

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_type=exc_tb, exc_val=exc_val, exc_tb=exc_tb)

    def execute(self, query, params=None):
        self.return_many_func = query.pop['return_many_func']
        self.return_one_func = query.pop['return_one_func']
        self.count_func = query.pop['count_func']
        self.enter_func = query.pop['enter_func']
        self.exit_func = query.pop['exit_func']
        self.model = query.pop['model']
        self.immediate_execute = query.pop['immediate_execute']
        self.pk = self.model._meta.pk_attname
        self.query = query
        self.params = params
        self.lastrowid = None
        if self.immediate_execute:
            self.objects = self.fetchone()
        return self

    def getlastrowid(self):
        lastrow = self.objects[-1]
        self.lastrowid = lastrow[self.pk]

    def fetchone(self):
        if not self.immediate_execute:
            [self.objects] = self.return_one_func(self.params, **self.query)
        if type(self.objects) != list:
            self.objects = [self.objects]
        self.getlastrowid()
        return self.objects

    def fetchmany(self, size=-1):
        if not self.immediate_execute:
            self.query['limit'] = self.query['offset'] + size
            self.objects = self.return_many_func(self.params, **self.query)
            self.getlastrowid()
        return self.objects

    def fetchall(self):
        if not self.immediate_execute:
            objects = self.return_many_func(self.params, **self.query)
            self.getlastrowid()
        return self.objects

    def rowcount(self):
        return self.count_func(self.params, **self.query)

    def start(self):
        self.enter_func()

    def close(self, **kwargs):
        self.exit_func(**kwargs)