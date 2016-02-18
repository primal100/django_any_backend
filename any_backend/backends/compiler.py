from django.db.models.sql import compiler

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

def make_query_dict(connection, query, immediate_execute):
    result = {
        'enter_func': connection.start,
        'exit_func': connection.close,
        'model': query.model
        'immediate_execute': False
    }
    return result

class SQLCompiler(compiler.SQLCompiler):

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        result = make_query_dict(self.connection, self.query, False)
        params = []
        result['return_many_func'] = self.connection.list
        result['return_one_func'] = self.connection.get
        result['count_func'] = self.connection.count
        self.subquery = subquery
        refcounts_before = self.query.alias_refcount.copy()
        try:
            extra_select, order_by, group_by = self.pre_sql_setup()
            distinct_fields = self.get_distinct()
            result['distinct'] = self.query.distinct

            from_, f_params = self.get_from_clause()

            result['app'], result['model_name'] = from_.split('.')
            result['app_model'] = from_

            params.extend(f_params)

            where, w_params = self.compile(self.where) if self.where is not None else ("", [])
            having, h_params = self.compile(self.having) if self.having is not None else ("", [])
            if where:
                params.extend(w_params)
            result['having'] = having
            params.extend(h_params)

            out_cols = []
            for _, (s_column, s_params), alias in self.select + extra_select:
                params.extend(s_params)
                out_cols.append(s_column)
            result['out_cols'] = out_cols

            grouping = []
            for g_sql, g_params in group_by:
                grouping.append(g_sql)
                params.extend(g_params)
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

    pass

class SQLInsertCompiler(compiler.SQLInsertCompiler):

    def as_sql(self):
        result = make_query_dict(self.connection, self.query, True)
        result['return_many_func'] = self.connection.create_bulk
        result['return_one_func'] = self.connection.create_bulk
        opts = self.query.get_meta()
        fields = self.query.fields if result['has_fields'] else [opts.pk]
        objs=[]
        for obj in self.query.objs:
            fields_values = {}
            for field in fields:
                fields_values[field.column] = self.pre_save_val(field, obj)
            objs.append(fields_values)
        params = objs
        return result, params

class SQLDeleteCompiler(compiler.SQLDeleteCompiler):

    def as_sql(self):
        result = make_query_dict(self.connection, self.query, True)
        result['return_many_func'] = self.connection.delete_bulk
        result['return_one_func'] = self.connection.delete_bulk

class SQLUpdateCompiler(compiler.SQLUpdateCompiler):
    pass