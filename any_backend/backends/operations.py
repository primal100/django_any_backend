from django.db.backends.base.operations import BaseDatabaseOperations

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