from django.core.cache import caches

class Cursor(object):

    def __init__(self):
        self.enter_func = None
        self.exit_func = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_type=exc_tb, exc_val=exc_val, exc_tb=exc_tb)

    def execute(self, query, params=None):
        if 'CREATE DATABASE' in query:
            self.func = params['func']
            self.enter_func = params['enter_func']
            self.exit_func = params['exit_func']
            db_name = query.split('CREATE DATABASE ')[1]
            self.func(db_name)
            return self
        elif 'CREATE TABLE' in query:
            self.enter_func = None
            self.exit_func = None
            return self
        else:
            self.func = query.pop('func')
            self.enter_func = query.pop('enter_func')
            self.exit_func = query.pop('exit_func')
            self.conversion_func = query.pop('conversion_func')
            self.model = query.pop('model')
            self.immediate_execute = query.pop('immediate_execute')
            self.pk_fieldname = self.model._meta.pk.attname
            self.fieldnames = [(self.pk_fieldname,)]
            self.pre_paginate_count = None
            db_config = query.pop('db_config')
            self.max_relation_depth = db_config.get('MAX_RELATION_DEPTH', 10)
            self.chunk_size = getattr(self.model._meta, 'chunk_size', None) or db_config.get('CHUNK_SIZE', None)
            cache_name = db_config.get('CACHE_NAME', None)
            if cache_name:
                self.cache = caches.get['CACHE_NAME']
                self.cache_timeout = db_config.get('CACHE_TIMEOUT', 60)
                self.cache_count_all_timeout = db_config.get('CACHE_COUNT_ALL_TIMEOUT', self.cache_timeout)
            else:
                self.cache = None
            self.query = query
            self.params = params
            self.pos = 0
            if self.immediate_execute:
                self.count = False
                self.results = self.func(self.model, self.params, **self.query)
                self.results = self.conversion_func(self.results, self.fieldnames)
                if self.cache:
                    self.cache.clear()
            else:
                self.results = []
                self.fields = query['out_cols']
                self.count = query.pop('count', None) or any('COUNT' in x.column for x in self.fields)
                self.fieldnames = []
                for field in self.fields:
                    field_model = field.model
                    if field_model == self.model:
                        field_tuple = (field.column,)
                    else:
                        field_tuple = tuple(self.get_related(field, field_model))
                    self.fieldnames.append(field_tuple)
                self.max = self.query['paginator'].limit or 1
            return self

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

    @property
    def lastrowid(self):
        if self.results:
            lastrow = self.results[-1]
            return lastrow[0]
        else:
            return None

    @property
    def rowcount(self):
        return len(self.results)

    def fetchone(self):
        if not self.immediate_execute:
            if self.count:
                self.fetchmany()
                return self.pre_paginate_count
        else:
            self.results = self.func(self.model, self.params, **self.query)
        result = [self.results[self.pos]]
        self.pos += 1
        return self.conversion_func(result, self.fieldnames)[0]

    def fetchmany(self, size=0):
        if self.immediate_execute:
            tuples = self.conversion_func(self.results, self.fieldnames)
            return tuples
        else:
            new_offset = self.query['paginator'].offset + self.pos
            new_limit = self.pos + size
            if new_limit > self.max:
                new_limit = self.max
            if new_offset > self.max:
                return []
            if not self.pre_paginate_count or new_offset <= max:
                self.query['paginator'].update_range(new_offset, new_limit)
                if self.cache:
                    self.results = self.cache.get(default=[], paginated=True)
                    self.pre_paginate_count = self.cache.get(default=(), paginated=False)
                    if self.results:
                        return self.results
                self.results, self.pre_paginate_count = self.func(self.model, self.params, **self.query)
                self.results = self.conversion_func(self.results, self.fieldnames)
                self.pre_paginate_count = (self.pre_paginate_count,)
                self.cache_set(self.results, paginated=True)
                self.cache_set(self.pre_paginate_count, paginated=False)
                self.pos += size
                if self.count:
                    return self.pre_paginate_count
                else:
                    return self.results
            else:
                return []


    def fetchall(self):
        return list(self.fetchmany())

    def cache_get(self, default=None, paginated=False):
        if self.cache:
            string = self.cache_get(self.func, paginated=paginated)
            return self.cache.get(string, default=default)
        return None

    def cache_set(self, value, paginated=False):
        if self.cache:
            if self.count and not self.params:
                timeout = self.cache_count_all_timeout
            else:
                timeout = self.cache_timeout
            string = self.cache_key(self.func)
            self.cache.set(string, value, timeout)

    def cache_key(self, func, paginated=False):
        query = self.query.copy()
        if not paginated:
            query['limit'] = query['offset'] = 0
        params = tuple(sorted(query.items()))
        query = tuple(sorted(query.items()))
        cache_string = str(query) + str(params) + self.func.__name__
        return cache_string

    def start(self):
        if self.enter_func:
            self.enter_func()

    def close(self, **kwargs):
        if self.exit_func:
            self.exit_func(**kwargs)