from any_backend.utils import get_db_by_name, convert_to_tuples
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
            self.model = query.pop('model')
            self.immediate_execute = query.pop('immediate_execute')
            self.pk_fieldname = self.model._meta.pk.attname
            self.field_names = [self.pk_fieldname]
            db_config = query.pop('db_config')
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
            if self.immediate_execute:
                self.count = False
                self.pos = 0
                self.results = self.func(self.model, self.params, **self.query)
                self.results = convert_to_tuples(self.results, self.field_names)
                if self.cache:
                    self.cache.clear()
            else:
                self.pos = query['paginator'].limit
                self.results = []
                self.fields = query['out_cols']
                for field in self.fields:
                    if field.column not in self.field_names:
                        self.field_names.append(field.column)
                self.count = any('COUNT' in x for x in self.field_names)
            return self

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
        return convert_to_tuples(result, self.field_names)[0]

    def fetchmany(self, size=-1):
        if self.immediate_execute:
            tuples = convert_to_tuples(self.results, self.field_names)
            return tuples
        func = self.func
        self.query['paginator'].update_range(self.pos, self.pos + size)
        if self.cache:
            self.results = self.cache.get(default=[], paginated=True)
            self.pre_paginate_count = self.cache.get(default=(), paginated=False)
            if self.results:
                return self.results
        self.results, self.pre_paginate_count = func(self.model, self.params, **self.query)
        self.results = convert_to_tuples(self.results, self.field_names)
        self.pre_paginate_count = (self.pre_paginate_count,)
        self.cache_set(self.results, paginated=True)
        self.cache_set(self.pre_paginate_count, paginated=False)
        self.pos += size
        return self.results

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