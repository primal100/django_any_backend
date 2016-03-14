from .features import DatabaseFeatures
from .creation import DatabaseCreation
from .database import Database
from .schema import DatabaseSchemaEditor
from .introspection import DatabaseIntrospection
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.validation import BaseDatabaseValidation
from django.utils.module_loading import import_string
from operations import DatabaseOperations
from importlib import import_module
from cursor import Cursor
import logging

logger = logging.getLogger('django')

class DatabaseWrapper(BaseDatabaseWrapper):
    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    is_non_db = True
    default_compiler = 'any_backend.backends.compiler'

    operators = {
        'exact': '= %s',
        'iexact': "LIKE %s ESCAPE '\\'",
        'contains': "LIKE %s ESCAPE '\\'",
        'icontains': "LIKE %s ESCAPE '\\'",
        'regex': 'REGEXP %s',
        'iregex': "REGEXP '(?i)' || %s",
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "LIKE %s ESCAPE '\\'",
        'endswith': "LIKE %s ESCAPE '\\'",
        'istartswith': "LIKE %s ESCAPE '\\'",
        'iendswith': "LIKE %s ESCAPE '\\'",
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.db_config = args[0]
        compiler_module = self.db_config.get('COMPILER', None) or self.default_compiler
        schema_module = self.db_config.get('SCHEMA', None)
        self.migrations = self.db_config.get('MIGRATIONS', False)
        if schema_module:
            self.SchemaEditorClass = import_string(schema_module + '.DatabaseSchemaEditor')
        self._cache = import_module(compiler_module)
        self.ops = DatabaseOperations(self, cache=self._cache)
        self.creation = DatabaseCreation(self)
        self.features = DatabaseFeatures(self)
        self.validation = BaseDatabaseValidation(self)
        client_class = self.db_config['CLIENT']
        client_class = import_string(client_class)
        self.db_name = self.db_config['NAME']
        self.client = client_class(self.db_config)
        introspection_module = self.db_config.get('INTROSPECTION', None)
        if introspection_module:
            self.introspectionClass = import_string(introspection_module + '.DatabaseIntrospection')
            self.introspection = self.introspectionClass(self)
        else:
            self.introspection = DatabaseIntrospection(self)
        logger.debug('Initialized django_any_backend. Compiler is %s. Client is %s.'
                     % (compiler_module, client_class))
        logger.debug('DB_config: %s' % self.db_config)

    def create_cursor(self):
        return Cursor()

    def get_connection_params(self):
        return{'connection': self.db_config}

    def get_new_connection(self, conn_params):
        if not self.schema_editor().db_exists(self.db_name):
            self.schema_editor().create_db(self.db_name)
        self.client.setup(self.db_name)
        return self.client

    def is_usable(self):
        return self.connection.check()

    def init_connection_state(self):
        pass

    def _set_autocommit(self, autocommit):
        pass
