from django.db.backends.base.operations import BaseDatabaseOperations
from django.utils.encoding import force_text
import six

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
        return None

    def quote_name(self, name):
        return name

    def last_executed_query(self, cursor, sql, params):
        """
        Returns a string of the query last executed by the given cursor, with
        placeholders replaced with actual values.

        `sql` is the raw query containing placeholders, and `params` is the
        sequence of parameters. These are used by default, but this method
        exists for database backends to provide a better implementation
        according to their own quoting schemes.
        """
        # Convert params to contain Unicode values.
        to_unicode = lambda s: force_text(s, strings_only=True, errors='replace')
        if isinstance(params, (list, tuple)):
            u_params = tuple(to_unicode(val) for val in params)
        elif params is None:
            u_params = ()
        else:
            u_params = str(params)

        return six.text_type("QUERY = %r - PARAMS = %r") % (sql, u_params)