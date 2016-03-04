from django.db.models.sql import compiler
from django.db.models.sql.constants import MULTI, NO_RESULTS, SINGLE, CURSOR
from django.core.exceptions import FieldError
from any_backend.paginators import BackendPaginator
from any_backend.filters import Filters, Filter
from any_backend.sorting import OrderingList
from django.core.cache import caches
from any_backend.distinct import DistinctFields
from any_backend.update import UpdateParams
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
                filter_obj = Filter(filter.lhs.field, filter.lookup_name, filter.rhs)
                filters.append(filter_obj)
        return filters

    def setup_attributes(self):
        self.setup_query()
        self.model = self.query.model
        self.pk_fieldname = self.model._meta.pk.attname
        self.fieldnames = [(self.pk_fieldname,)]
        self.db_config = self.connection.settings_dict
        self.max_relation_depth = self.db_config.get('MAX_RELATION_DEPTH', 10)
        self.chunk_size = getattr(self.model._meta, 'chunk_size', None) or self.db_config.get('CHUNK_SIZE', float('inf'))
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
                return field_tuple
            else:
                field_tuple.insert(0, field_model._meta.model_name)
                field_tuple += self.get_related(field, relation.model)
                return field_tuple

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False, count=False):
        result, params = {}, {}

        filters = self.get_filters(self.query.where) if self.query.where is not None else ([])

        distinct = DistinctFields()
        distinct += self.get_distinct()
        result['distinct'] = distinct

        if not count:

            result['out_cols'] = self.fields

            ordering = OrderingList()
            pk_attname = self.query.model._meta.pk.attname
            for i, order_by in enumerate(self.query.order_by):
                if order_by == 'pk':
                    self.query.order_by[i] = pk_attname
                elif order_by == '-pk':
                    self.query.order_by[i] = '-' + pk_attname
            ordering += self.query.order_by
            result['order_by'] = ordering

            result['paginator'] = BackendPaginator(with_limits, self.query.low_mark, self.query.high_mark,
                                                   self.connection.ops.no_limit_value())

        return result, filters

    def get_list(self, query, params, page_size, fieldnames):
        results = []
        remaining = page_size
        pos = 0
        pre_paginate_count = 0
        logger.debug('Retrieving result list. Page_size: %s. Chunk_size: %s' % (page_size, self.chunk_size))
        while remaining > 0:
            if self.chunk_size < remaining:
                query['paginator'].update(pos, self.chunk_size)
            else:
                query['paginator'].update(pos, remaining)
            with self.connection.client as client:
                chunk_results, pre_paginate_count = client.list(self.model, params, **query)
                chunk_results = self.connection.client.convert_to_tuples(chunk_results, fieldnames)
                results += chunk_results
                if page_size == float('inf'):
                    page_size = pre_paginate_count
                if self.chunk_size == float('inf'):
                    remaining = 0
                else:
                    pos += self.chunk_size
                    remaining = page_size - pos
                    if len(chunk_results) < self.chunk_size  or len(results) >= page_size:
                        remaining = 0
                logger.debug('Chunk retrieved. %s Remaining. Pos: %s. Pre-paginated count: %s' % (
                remaining, pos, pre_paginate_count[0]))
                logger.debug(chunk_results)

        pre_paginate_count = (pre_paginate_count,)
        return results, pre_paginate_count

    def execute_sql(self, result_type=MULTI):
        if not result_type:
            result_type = NO_RESULTS

        self.setup_attributes()

        if self.model._meta.db_table == 'django_migrations':
            return []

        count = False
        self.fields = []
        for column in self.select:
            field = column[0]._output_field
            if hasattr(field, 'column'):
               self.fields.append(field)
            elif 'count' in str(column):
                count = True

        query, params = self.as_sql(count=count)

        if count:
            column_names = 'column_names=count'
            key = self.cache_key(query, params, column_names, count=True)
            with self.connection.client as client:
                results = (client.count(self.model, params, **query),)
        else:
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
            if result_type == SINGLE:
                page_size = 1
                self.chunk_size = 1
                query['paginator'].update(0, page_size)
            else:
                if query['paginator'].paginated:
                    page_size = query['paginator'].page_size
                else:
                    page_size = float('inf')
            key = self.cache_key(query, params, column_names)
            count_key = self.cache_key(query, params, 'column_names=count', True)
            results = self.cache_get(key)
            pre_paginate_count = self.cache_get(count_key)
            if results is None or pre_paginate_count is None:
                results, pre_paginate_count = self.get_list(query, params, page_size, fieldnames)
                self.cache_set(key, results)
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

    def cache_key(self, query, params, column_names, count=False):
        model_name = self.model._meta.model_name
        if count:
            if not params and not query['distinct']:
                return 'Count_All;' + model_name
            else:
                prefix = 'Count'
                paginator = ''
        else:
            prefix = 'List'
            paginator = query['paginator']
        key = prefix + ';' + model_name + ';' + str(params) + ';' + str(
            query['distinct']) + ';' + str(column_names) + ';' + str(
            paginator) + ';' + str(query['order_by'])
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
        return objs

    def execute_sql(self, return_id=False):
        if self.model._meta.db_table == 'django_migrations':
            return []
        assert not (return_id and len(self.query.objs) != 1)
        self.return_id = return_id
        self.setup_attributes()
        objects = self.as_sql()
        logger.debug('Creating objects: %s' % objects)
        with self.connection.client as client:
            pks = client.create_bulk(self.model, objects)
        self.cache.clear()
        if not (return_id and client):
            return
        return pks[-1]

class SQLDeleteCompiler(compiler.SQLDeleteCompiler, CompilerMixin):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        self.setup_attributes()
        filters = self.get_filters(self.query.where) if self.query.where is not None else ([])
        return filters

    def execute_sql(self, result_type=MULTI):
        if self.model._meta.db_table == 'django_migrations':
            return 0
        self.setup_attributes()
        filters = self.as_sql()
        logger.debug('Deleting objects: %s' % filters)
        with self.connection.client as client:
            rows = client.delete_bulk(self.model, filters)
        self.cache.clear()
        return rows

class SQLUpdateCompiler(compiler.SQLUpdateCompiler, CompilerMixin):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        self.setup_attributes()
        result = {}
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
        result['update_with'] = update_with
        filters = self.get_filters(self.query.where)[0] if self.query.where is not None else ([])
        return result, filters

    def execute_sql(self, result_type):
        if self.model._meta.db_table == 'django_migrations':
            return 0
        self.setup_attributes()
        query, filters = self.as_sql()
        logger.debug('Updating objects %s' % filters)
        with self.connection.client as client:
            rows = client.update_bulk(self.model, filters, **query)
        self.cache.clear()
        return rows

class SQLAggregateCompiler(compiler.SQLAggregateCompiler, CompilerMixin):
    def as_sql(self):
        self.setup_attributes()

    def execute_sql(self, result_type=MULTI):
        logger.debug('Counting model: ' % self.model)
        with self.connection.client as client:
            count = client.count(self.model)
        return count