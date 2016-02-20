from django.db.models.sql import compiler
from django.core.exceptions import FieldError
from any_backend.utils import get_db_by_name
from any_backend.paginators import BackendPaginator
from any_backend.filters import Filters, Filter
from any_backend.sorting import OrderBy, OrderingList
from any_backend.distinct import DistinctFields
from any_backend.update import UpdateParams

def make_dicts(connection, query, immediate_execute):
    result = {
        'enter_func': connection.start,
        'exit_func': connection.close,
        'model': query.model,
        'immediate_execute': immediate_execute,
        'db_config': get_db_by_name(query.using)
    }
    params = {}
    return result, params


class SQLCompiler(compiler.SQLCompiler):

    def compile(self, node, select_format=False):
        filters = Filters()
        for filter in node.children:
            filter_obj = Filter(filter.lhs.field, filter.lookup_name, filter.rhs)
            filters.append(filter_obj)
        return filters

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result, params = make_dicts(self.connection, self.query, None)
        result['func'] = self.connection.list
        self.subquery = subquery
        refcounts_before = self.query.alias_refcount.copy()
        try:
            extra_select, order_by, group_by = self.pre_sql_setup()

            distinct = DistinctFields()
            distinct += self.get_distinct()
            result['distinct'] = distinct

            from_, f_params = self.get_from_clause()

            result['app'], result['model_name'] = from_.split('.')
            result['app_model'] = from_

            filters = self.compile(self.where) if self.where is not None else ([])

            out_cols = []
            for _, (s_column, s_params), alias in self.select + extra_select:
                out_cols.append(s_column)
            result['out_cols'] = out_cols

            ordering = OrderingList()
            if order_by:
                for _, (o_sql, o_params, _) in order_by:
                    orderby = OrderBy(**o_sql)
                    ordering.append(order_by)
            result['order_by'] = ordering

            result['paginator'] = BackendPaginator(with_limits, self.query.high_mark, self.query.low_mark,
                                                   self.connection.ops.no_limit_value())

            return result, filters
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)


class SQLInsertCompiler(compiler.SQLInsertCompiler):

    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, None)
        result['func'] = self.connection.create_bulk
        opts = self.query.get_meta()
        fields = self.query.fields if result['has_fields'] else [opts.pk]
        objs=[]
        for obj in self.query.objs:
            fields_values = {}
            for field in fields:
                fields_values[field.column] = self.pre_save_val(field, obj)
            objs.append(fields_values)
        result['results'] = objs
        return result, params

class SQLDeleteCompiler(compiler.SQLDeleteCompiler):

    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.delete_bulk
        filters = self.compile(self.where) if self.where is not None else ([])
        return result, filters

class SQLUpdateCompiler(compiler.SQLUpdateCompiler):

    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.update_bulk
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
        filters = self.compile(self.where) if self.where is not None else ([])
        return result, filters

class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.count
        pass