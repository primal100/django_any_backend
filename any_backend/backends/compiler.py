from django.db.models.sql import compiler
from django.core.exceptions import FieldError
from any_backend.paginators import BackendPaginator
from any_backend.filters import Filters, Filter
from any_backend.sorting import OrderBy, OrderingList
from any_backend.distinct import DistinctFields
from any_backend.update import UpdateParams

def make_dicts(connection, query, immediate_execute):
    result = {
        'enter_func': connection.client.enter,
        'exit_func': connection.client.close,
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
            filter_obj = Filter(filter.lhs.field, filter.lookup_name, filter.rhs)
            filters.append(filter_obj)
        return filters

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result, params = make_dicts(self.connection, self.query, False)
        result['func'] = self.connection.client.list
        self.subquery = subquery
        refcounts_before = self.query.alias_refcount.copy()
        try:
            #extra_select, order_by, group_by = self.pre_sql_setup()

            self.setup_query()

            distinct = DistinctFields()
            distinct += self.get_distinct()
            result['distinct'] = distinct

            filters = self.compile(self.query.where) if self.query.where is not None else ([])

            out_cols = []
            for column in self.select:
                out_cols.append(column[0]._output_field)
            result['out_cols'] = out_cols

            ordering = OrderingList()
            """if order_by:
                for _, (o_sql, o_params, _) in order_by:
                    orderby = OrderBy(**o_sql)
                    ordering.append(order_by)"""
            result['order_by'] = ordering

            result['paginator'] = BackendPaginator(with_limits, self.query.high_mark, self.query.low_mark,
                                                   self.connection.ops.no_limit_value())

            return result, filters
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)


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
        pass