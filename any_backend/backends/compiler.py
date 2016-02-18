from django.db.models.sql import compiler
from django.core.exceptions import FieldError

class Client(object):
    """
    Initialized and setup function run when first connection is made after Django application starts.
    Can be accessed from within most functions in the other classes as self.using
    """
    def setup(self):
        pass

class DictToObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def make_dicts(connection, query, immediate_execute, using):
    result = {
        'enter_func': connection.start,
        'exit_func': connection.close,
        'model': query.model,
        'immediate_execute': False,
        'db_config': query.using
    }
    params = {}
    return result, params

class SQLCompiler(compiler.SQLCompiler):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result, params = make_dicts(self.connection, self.query, None)
        result['func'] = self.connection.list
        self.subquery = subquery
        refcounts_before = self.query.alias_refcount.copy()
        try:
            extra_select, order_by, group_by = self.pre_sql_setup()
            distinct_fields = self.get_distinct()
            result['distinct'] = self.query.distinct

            from_, f_params = self.get_from_clause()

            result['app'], result['model_name'] = from_.split('.')
            result['app_model'] = from_

            """params.extend(f_params)

            where, w_params = self.compile(self.where) if self.where is not None else ("", [])
            having, h_params = self.compile(self.having) if self.having is not None else ("", [])
            if where:
                params.extend(w_params)
            result['having'] = having
            params.extend(h_params)"""

            out_cols = []
            for _, (s_column, s_params), alias in self.select + extra_select:
                #params.extend(s_params)
                out_cols.append(s_column)
            result['out_cols'] = out_cols

            grouping = []
            for g_sql, g_params in group_by:
                grouping.append(g_sql)
                #params.extend(g_params)
            if grouping:
                if distinct_fields:
                    raise NotImplementedError(
                        "annotate() + distinct(fields) is not implemented.")
                if not order_by:
                    order_by = self.connection.ops.force_no_ordering()
            result['group_by'] = grouping

            ordering = []
            if order_by:
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
            result['order_by'] = ordering

            if with_limits:
                if self.query.high_mark is not None:
                    result['limit'] = self.query.high_mark - self.query.low_mark
                else:
                    result['limit'] = None
                if self.query.low_mark:
                    if self.query.high_mark is None:
                        val = self.connection.ops.no_limit_value()
                        if val:
                            result['limit'] = val
                result['offset'] = self.query.low_mark

            return result, params
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
        return result, params

class SQLUpdateCompiler(compiler.SQLUpdateCompiler):

    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.update_bulk
        field_values = {}
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
            field_values[name] = val
        if not field_values:
            return '', ()
        result['field_values'] = field_values
        return result, params

class SQLAggregateCompiler(compiler.SQLAggregateCompiler):
    def as_sql(self):
        result, params = make_dicts(self.connection, self.query, True)
        result['func'] = self.connection.count
        pass