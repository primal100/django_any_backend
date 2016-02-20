from any_backend.utils import get_db_by_name, convert_to_tuples
from django.core.cache import caches

class Cursor(object):

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_type=exc_tb, exc_val=exc_val, exc_tb=exc_tb)

    def execute(self, query, params=None):
        self.func = query['func']
        self.enter_func = query['enter_func']
        self.exit_func = query['exit_func']
        self.model = query['model']
        self.field_names = query['out_cols']
        self.count = any('COUNT' in x for x in self.field_names)
        self.immediate_execute = query['immediate_execute']
        self.pk_attname = self.model._meta.pk_attname
        db_config = query['db_config']
        self.chunk_size = getattr(self.model._meta, 'chunk_size', None) or db_config.get('CHUNK_SIZE', None)
        cache_name = db_config.get('CACHE_NAME', None)
        self.cache = caches.get(cache_name, None)
        self.cache_timeout = db_config.get('CACHE_TIMEOUT', 60)
        self.cache_count_all_timeout = db_config.get('CACHE_COUNT_ALL_TIMEOUT', self.cache_timeout)
        self.query = query
        self.params = params
        self.lastrowid = None
        if self.immediate_execute:
            self.results = self.func(self.params, **self.query)
            self.getlastrowid()
            self.cache.clear()
        else:
            self.results = []
        return self

    def getlastrowid(self):
        lastrow = self.results[-1]
        self.lastrowid = lastrow[self.pk_attname]

    def fetchone(self):
        if not self.immediate_execute:
            if self.count:
                self.fetchmany()
                return self.pre_paginate_count
        else:
            self.results = self.func(self.params, **self.query)
        self.getlastrowid()
        result = [self.results[0]]
        return convert_to_tuples(result, self.field_names)[0]

    def fetchmany(self, size=-1):
        if self.immediate_execute:
            yield convert_to_tuples(self.results, self.field_names)
        else:
            func = self.func
            if self.cache:
                self.results = self.cache.get(default=[], paginated=True)
                self.pre_paginate_count = self.cache.get(default=(), paginated=False)
            else:
                self.results, self.pre_paginate_count = [], ()
            if self.results:
                yield self.results
            else:
                self.results = results = []
                chunk_size = self.chunk_size or size
                max = self.query['limit']
                self.query['limit'] = self.query['offset'] + chunk_size
                while self.query['limit'] <= max:
                    results, self.pre_paginate_count = func(self.params, **self.query)
                    results = convert_to_tuples(results, self.field_names)
                    self.results += results
                    self.query['limit'] += chunk_size
                    self.query['offset'] += chunk_size
                    yield results
                self.pre_paginate_count = (self.pre_paginate_count,)
                self.cache_set(self.results, paginated=True)
                self.cache_set(self.pre_paginate_count, paginated=False)
            self.getlastrowid()

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

    def rowcount(self):
        return len(self.results)

    def start(self):
        self.enter_func()

    def close(self, **kwargs):
        self.exit_func(**kwargs)