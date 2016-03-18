from django.db.backends.base.operations import BaseDatabaseOperations
from cursor import CursorRequest

class DatabaseOperations(BaseDatabaseOperations):
    def __init__(self, connection, cache=None):
        super(DatabaseOperations, self).__init__(connection)
        self._cache = cache

    def compiler(self, compiler_name):
        """
        Returns the SQLCompiler class corresponding to the given name,
        in the namespace corresponding to the `compiler_module` attribute
        on this backend.
        """
        if self._cache is None:
            raise ImportError('Compiler classes were not imported. Make sure a valid compiler module string is set in your DatabaseWrapper')
        return getattr(self._cache, compiler_name)

    def no_limit_value(self):
        if 'NO_LIMIT_VALUE' in self.connection.db_config:
            return self.connection.db_config['NO_LIMIT_VALUE']
        return 1000

    def quote_name(self, name):
        return name

    def last_executed_query(self, cursor, sql, params):
        query = str(sql)
        return query

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        for table in tables:
            key = 'DELETE %s' % (table)
            request = CursorRequest(self.connection.client.flush, key, table, sequences, allow_cascade)
            yield request
