from django.db.models.sql import compiler
from django.db.models.sql.constants import (
    MULTI, NO_RESULTS, SINGLE, CURSOR
)
from django.core.exceptions import FieldError
from any_backend.paginators import BackendPaginator
from any_backend.filters import Filters, Filter
from any_backend.sorting import OrderBy, OrderingList
from django.core.cache import caches
from any_backend.distinct import DistinctFields
from any_backend.update import UpdateParams
import logging

logger = logging.getLogger('django')

def make_dicts(connection, query, immediate_execute):
    result = {
        'enter_func': connection.client.enter,
        'exit_func': connection.client.close,
        'conversion_func': connection.client.convert_to_tuples,
        'model': query.model,
        'immediate_execute': immediate_execute,
        'db_config': connection.settings_dict
    }
    params = {}
    return result, params


class SQLCompiler(compiler.SQLCompiler):

    def compile(self, node, select_format=False):
        filters = Filters()
        node_children = getattr(node, 'children', [])
        for filter in node_children:
            if hasattr(filter, 'lhs') and hasattr(filter, 'rhs'):
                filter_obj = Filter(filter.lhs.field, filter.lookup_name, filter.rhs)
                filters.append(filter_obj)
        return filters

    def setup_attributes(self):
        self.model = self.query.model
        self.pk_fieldname = self.model._meta.pk.attname
        self.fieldnames = [(self.pk_fieldname,)]
        self.db_config = self.connection.settings_dict
        self.max_relation_depth = self.db_config.get('MAX_RELATION_DEPTH', 10)

    def setup_read_query(self):
        self.chunk_size = getattr(self.model._meta, 'chunk_size', None) or self.db_config.get('CHUNK_SIZE', None)
        cache = self.db_config.get('CACHE', None)
        if cache:
            cache_name = cache['NAME']
            self.cache = caches[cache_name]
            self.cache_timeout = cache.get('TIMEOUT', 60)
            self.cache_count_all_timeout = cache.get('COUNT_ALL_TIMEOUT', self.cache_timeout)
        else:
            self.cache = None

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

        self.setup_query()

        filters = self.compile(self.query.where) if self.query.where is not None else ([])

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

    def execute_sql(self, result_type=MULTI):
        if not result_type:
            result_type = NO_RESULTS

        self.setup_attributes()

        if self.model._meta.db_table == 'django_migrations':
            return []

        self.setup_read_query()

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
            with self.connection.client as client:
                results = (client.count(self.model, params, **query),)
        else:
            self.column_names = 'column_names='
            fieldnames = []
            for field in self.fields:
                field_model = field.model
                if field_model == self.model:
                    field_tuple = (field.column,)
                else:
                    field_tuple = tuple(self.get_related(field, field_model))
                self.column_names += field.column + ';'
                fieldnames.append(field_tuple)
            if result_type == SINGLE:
                paginated = True
                page_size = 1
                self.chunk_size = 1
                query['paginator'].update(0, page_size)
            else:
                paginated = query['paginator'].paginated
                if paginated:
                    page_size = query['paginator'].page_size
                else:
                    page_size = float('inf')
            full_results = []
            results = None
            pre_paginate_count = 0
            pos = 0
            while results != []:
                remaining = page_size - pos
                if self.chunk_size < remaining:
                    query['paginator'].update(pos, self.chunk_size)
                else:
                    query['paginator'].update(pos, remaining)
                with self.connection.client as client:
                    results, pre_paginate_count = client.list(self.model, params, **query)
                    results = self.connection.client.convert_to_tuples(results, fieldnames)
                full_results += results
                if page_size == float('inf'):
                    page_size = pre_paginate_count
                pos += self.chunk_size
                if len(results) < self.chunk_size or self.chunk_size == page_size or pos > page_size or len(
                        full_results) >= page_size:
                    results = []


            pre_paginate_count = (pre_paginate_count,)

        if result_type == SINGLE:
            return results[0]

        if result_type == CURSOR:
            return self.connection.client

        if result_type == NO_RESULTS:
            return

        return results

class SQLInsertCompiler(compiler.SQLInsertCompiler):

    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.client.create_bulk
        opts = self.query.get_meta()
        has_fields = getattr(result, 'has_fields', None)
        fields = self.query.fields if 'has_fields' else [opts.pk]
        objs=[]
        for obj in self.query.objs:
            fields_values = {}
            for field in fields:
                fields_values[field.column] = self.pre_save_val(field, obj)
            objs.append(fields_values)
        params = objs
        return [[result, params]]

class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.client.delete_bulk
        filters = self.compile(self.query.where) if self.query.where is not None else ([])
        return result, filters

class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.client.update_bulk
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
        filters = self.compile(self.query.where)[0] if self.query.where is not None else ([])
        return result, filters

class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.client.count

def cursor_iter(cursor, sentinel, col_count):
    """
    Yields blocks of rows from a cursor and ensures the cursor is closed when
    done.
    """
    try:
        for rows in iter((lambda: cursor.fetchmany(GET_ITERATOR_CHUNK_SIZE)),
                         sentinel):
            yield [r[0:col_count] for r in rows]
    finally:
        cursor.close()