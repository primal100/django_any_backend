from django.db.models.sql import compiler
from django.db.models.sql.constants import MULTI, NO_RESULTS, SINGLE, CURSOR
from django.core.exceptions import FieldError
from any_backend.paginators import BackendPaginator
from any_backend.filters import Filters, Filter
from any_backend.sorting import OrderingList
from django.core.cache import caches
from any_backend.distinct import DistinctFields
from any_backend.update import UpdateParams
from cursor import CursorRequest
import logging

logger = logging.getLogger('django')

class CompilerMixin(object):

    def __init__(self, query, connection):
        self.query = query
        self.connection = connection

    def get_filters(self, node):
        filters = Filters()
        node_children = getattr(node, 'children', [])
        for filter in node_children:
            if hasattr(filter, 'lhs') and hasattr(filter, 'rhs'):
                filter_obj = Filter(filter.lhs.field, filter.lookup_name, node.negated, filter.rhs)
                filters.append(filter_obj)
        return filters

    def setup_attributes(self):
        self.setup_query()
        self.model = self.query.model
        self.pk_fieldname = self.model._meta.pk.attname
        self.fieldnames = [(self.pk_fieldname,)]
        self.db_config = self.connection.settings_dict
        self.max_relation_depth = self.db_config.get('MAX_RELATION_DEPTH', 10)
        self.chunk_size = getattr(self.model, 'max_per_request', None) or self.db_config.get('CHUNK_SIZE', float('inf'))
        cache = self.db_config.get('CACHE', None)
        if cache:
            cache_name = cache['NAME']
            self.cache = caches[cache_name]
            self.cache_timeout = cache.get('TIMEOUT', 60)
            self.cache_count_all_timeout = cache.get('COUNT_ALL_TIMEOUT', self.cache_timeout)
            logger.debug('Using cache: %s' % cache_name)
        else:
            self.cache = None
            logger.debug('Caching not enabled')

class SQLCompiler(compiler.SQLCompiler, CompilerMixin):

    def get_related(self, field, field_model):
        field_tuple = [field_model._meta.model_name]
        for relation in field_model._meta._relation_tree:
            if relation.model == self.model:
                field_tuple.append(field.column)
            else:
                field_tuple.insert(0, field_model._meta.model_name)
                field_tuple += self.get_related(field, relation.model)
        return field_tuple

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        query, params = {}, {}

        filters = self.get_filters(self.query.where) if self.query.where is not None else ([])

        distinct = DistinctFields()
        distinct += self.get_distinct()
        query['distinct'] = distinct

        count = False
        self.fields = []
        for column in self.select:
            field = column[0]._output_field
            if hasattr(field, 'column'):
               self.fields.append(field)
            elif 'count' in str(column):
                count = True

        if count:
            key = self.key(query, filters, '', count=True)
            request = CursorRequest(self.connection.client.count, key, self.model, filters, **query)
        else:
            query['out_cols'] = self.fields
            column_names = 'column_names='
            fieldnames = []
            for field in self.fields:
                field_model = field.model
                if field_model == self.model:
                    field_tuple = (field.column,)
                else:
                    field_tuple = tuple(self.get_related(field, field_model))
                column_names += field.column + ';'
                fieldnames.append(field_tuple)
            ordering = OrderingList()
            pk_attname = self.query.model._meta.pk.attname
            for i, order_by in enumerate(self.query.order_by):
                if order_by == 'pk':
                    self.query.order_by[i] = pk_attname
                elif order_by == '-pk':
                    self.query.order_by[i] = '-' + pk_attname
            ordering += self.query.order_by
            query['order_by'] = ordering

            query['paginator'] = self.paginator

            key = self.key(query, filters, column_names)
            request = CursorRequest(get_list, key, self.connection, key, self.model, filters, query, fieldnames,
                                    self.page_size, self.chunk_size)
        return request, count

    def execute_sql(self, result_type=MULTI):
        if not result_type:
            result_type = NO_RESULTS

        self.setup_attributes()

        if not self.connection.migrations and self.model._meta.db_table == 'django_migrations':
            return []

        self.paginator = BackendPaginator(True, self.query.low_mark, self.query.high_mark,
                                                   self.connection.ops.no_limit_value())
        if result_type == SINGLE:
            self.query.high_mark = self.query.low_mark + 1
            self.page_size = 1
        else:
            if self.paginator.paginated:
                self.page_size = self.paginator.page_size
            else:
                self.page_size = float('inf')

        request, count = self.as_sql()

        if count:
            results = self.cache_get(request.key)
            if not results:
                with self.connection.cursor() as cursor:
                    result = cursor.execute(request)
                    results = [((result),)]
                    self.cache_set(request.key, results)
        else:
            count_key = self.key(request.args[4], request.kwargs, 'column_names=count', True)
            results = self.cache_get(request.key)
            pre_paginate_count = self.cache_get(count_key)
            if results is None or pre_paginate_count is None:
                with self.connection.cursor() as cursor:
                    results, pre_paginate_count = cursor.execute(request)
                self.cache_set(request.key, results)
                self.cache_set(count_key, pre_paginate_count)

        if result_type == SINGLE:
            if len(results) > 0:
                return results[0][0:self.col_count]
            return None

        if result_type == CURSOR:
            return self.connection.client

        if result_type == NO_RESULTS:
            return

        return results

    def key(self, query, params, column_names, count=False):
        model_name = self.model._meta.db_table
        if count:
            if not params and not query['distinct']:
                return 'Count_All;' + model_name
            else:
                prefix = 'Count'
                paginator = ''
                order_by = ''
        else:
            prefix = 'List'
            order_by = query['order_by']
            paginator = query['paginator']
        key = '%s;%s;%s;%s;%s;%s;%s' % (prefix, model_name, params, query['distinct'], column_names, paginator, order_by)
        key = key.strip()
        logger.debug(key)
        return key

    def cache_get(self, key):
        if self.cache:
            logger.debug('Checking cache for key %s ' % key)
            return self.cache.get(key, default=None)
        return None

    def cache_set(self, key, value):
        if self.cache:
            if key.startswith('Count_All'):
                timeout = self.cache_count_all_timeout
            else:
                timeout = self.cache_timeout
            logger.debug('Setting cache with key: %s, value: %s' % (key, value))
            self.cache.set(key, value, timeout)

class SQLInsertCompiler(compiler.SQLInsertCompiler, CompilerMixin):

    def as_sql(self):
        opts = self.query.get_meta()
        has_fields = bool(self.query.fields)
        fields = self.query.fields if has_fields else [opts.pk]
        objs=[]
        for obj in self.query.objs:
            fields_values = {}
            for field in fields:
                fields_values[field.column] = self.pre_save_val(field, obj)
            objs.append(fields_values)
        key = self.key(objs)
        request = CursorRequest(self.connection.client.create_bulk, key, self.model, objs)
        return request

    def execute_sql(self, return_id=False):
        assert not (return_id and len(self.query.objs) != 1)
        self.return_id = return_id
        self.setup_attributes()
        if not self.connection.migrations and self.model._meta.db_table == 'django_migrations':
            return []
        request = self.as_sql()
        with self.connection.cursor() as cursor:
            pks = cursor.execute(request)
        self.cache.clear()
        if not (return_id and cursor):
            return
        return pks[-1]

    def key(self, objs):
        model_name = self.model._meta.db_table
        prefix = 'Create'
        key = "%s;%s: %s" % (prefix, model_name, objs)
        return key

class SQLDeleteCompiler(compiler.SQLDeleteCompiler, CompilerMixin):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        self.setup_attributes()
        filters = self.get_filters(self.query.where) if self.query.where is not None else ([])
        key = self.key(filters)
        request = CursorRequest(self.connection.client.delete_bulk, key, self.model, filters)
        return request

    def execute_sql(self, result_type=MULTI):
        self.setup_attributes()
        if not self.connection.migrations and self.model._meta.db_table == 'django_migrations':
            return []
        request = self.as_sql()
        with self.connection.cursor as cursor:
            rows = cursor.execute(request)
            self.cache.clear()
            if result_type == CURSOR:
                return cursor
        return rows

    def key(self, filters):
        model_name = self.model._meta.db_table
        prefix = 'Delete'
        key = '%s;%s;%s;' % (prefix, model_name, filters)
        return key

class SQLUpdateCompiler(compiler.SQLUpdateCompiler, CompilerMixin):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        self.setup_attributes()
        update_with = UpdateParams()
        for field, model, val in self.query.values:
            if hasattr(val, 'resolve_expression'):
                val = val.resolve_expression(self.query, allow_joins=False, for_save=True)
                if val.contains_aggregate:
                    raise FieldError("Aggregate functions are not allowed in this query")
            elif hasattr(val, 'prepare_database_save'):
                if field.remote_field:
                    val = field.get_db_prep_save(
                        val.prepare_database_save(field),
                        connection=self.connection,
                    )
                else:
                    raise TypeError(
                        "Tried to update field %s with a model instance, %r. "
                        "Use a value compatible with %s."
                        % (field, val, field.__class__.__name__)
                    )
            else:
                val = field.get_db_prep_save(val, connection=self.connection)

            name = field.column
            update_with[name] = val
        if not update_with:
            return '', ()
        query = {'update_with': update_with}
        filters = self.get_filters(self.query.where)[0] if self.query.where is not None else ([])
        key = self.key(filters, query)
        request = CursorRequest(self.connection.client.update_bulk, key, self.model, filters, **query)
        return request

    def key(self, filters, query):
        model_name = self.model._meta.db_table
        prefix = 'Update'
        key = '%s;%s;%s;%s;' % (prefix, model_name, filters, query['update_with'])
        return key

    def execute_sql(self, result_type):
        self.setup_attributes()
        if not self.connection.migrations and self.model._meta.db_table == 'django_migrations':
            return 0
        request = self.as_sql()
        with self.connection.cursor() as cursor:
            rows = cursor.execute(request)
        self.cache.clear()
        if result_type == CURSOR:
            return self.connection.cursor
        return rows

class SQLAggregateCompiler(compiler.SQLAggregateCompiler, CompilerMixin):
    def as_sql(self):
        self.setup_attributes()
        key = self.key()
        return CursorRequest(self.connection.client.count, key, self.model)

    def execute_sql(self, result_type=MULTI):
        request = self.as_sql()
        with self.connection.cursor as cursor:
            count = cursor.execute(request)
        if result_type == SINGLE:
            return count
        elif result_type == CURSOR:
            return cursor
        return (count,)

    def key(self):
        model_name = self.model._meta.db_table
        prefix = 'Aggregate Count'
        key = '%s;%s;' % (prefix, model_name)
        return key


def get_list(connection, key, model, filters, query, fieldnames, page_size, chunk_size):
    results = []
    remaining = page_size
    pos = 0
    pre_paginate_count = 0
    logger.debug('Retrieving result list. Page_size: %s. Chunk_size: %s' % (page_size, chunk_size))
    while remaining > 0:
        if chunk_size < remaining:
            query['paginator'].update(pos, chunk_size)
        else:
            query['paginator'].update(pos, remaining)
        key = '%s, pos=%s' % (key, pos)
        request = CursorRequest(connection.client.list, key, model, filters, **query)
        with connection.cursor() as cursor:
            chunk_results, pre_paginate_count = cursor.execute(request)
            chunk_results = connection.client.convert_to_tuples(chunk_results, fieldnames)
            results.append(chunk_results)
            if page_size == float('inf'):
                self.page_size = pre_paginate_count
            if chunk_size == float('inf'):
                remaining = 0
            else:
                pos += chunk_size
                remaining = page_size - pos
                if len(chunk_results) < chunk_size or sum([len(x) for x in results]) >= page_size:
                    remaining = 0
            logger.debug('Chunk retrieved. %s Remaining. Pos: %s. Pre-paginated count: %s' % (
            remaining, pos, pre_paginate_count))
            logger.debug(chunk_results)

    pre_paginate_count = (pre_paginate_count,)

    return results, pre_paginate_count