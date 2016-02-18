from any_backend.utils import get_db_by_name
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
        self.immediate_execute = query['immediate_execute']
        self.pk_attname = self.model._meta.pk_attname
        db_config = get_db_by_name(query['db_config'])
        self.chunk_size = getattr(self.model._meta, 'chunk_size', None) or db.get('CHUNK_SIZE', None)
        cache_name = db_config.get('CACHE_NAME', None)
        self.cache = caches.get(cache_name, None)
        self.cache_timeout = db_config.get('CACHE_TIMEOUT', 60)
        self.cache_count_all_timeout = db_config.get('CACHE_COUNT_ALL_TIMEOUT', self.cache_timeout)
        self.query = query
        self.params = params
        self.lastrowid = None
        if self.immediate_execute:
            self.results = self.func(self.params, **self.query)
        else:
            self.results = []
        return self

    def getlastrowid(self):
        lastrow = self.results[-1]
        self.lastrowid = lastrow[self.pk_attname]


    def fetchone(self):
        if not self.immediate_execute:
            self.results = self.func(self.params, **self.query)
        if any(type(self.results) == x for x in [list, tuple]):
            self.results = (self.results[0],)
        else:
            self.results =
        self.getlastrowid()
        return self.results

    def fetchmany(self, size=-1):
        if self.immediate_execute:
            yield self.results
        else:
            func = self.func
            if self.cache:
                cache_string = self.cache_request(func)
                results, pre_paginate_count = self.cache.get(cache_string, default=[[], None])
            else:
                results, pre_paginate_count = [], None
            if results:
                yield results
            else:
                chunk_size = self.chunk_size or size
                max = self.query['limit']
                self.query['limit'] = self.query['offset'] + chunk_size
                while self.query['limit'] <= max:
                    results, pre_paginate_count = func(self.params, **self.query)
                    results += results
                    self.query['limit'] += chunk_size
                    self.query['offset'] += chunk_size
                    yield results
                self.cache_result(func, [results, pre_paginate_count])
            self.results = results
            self.getlastrowid()

    def fetchall(self):
        return list(self.fetchmany())

    def cache_result(self, func, value, timeout):
        if self.cache:
            if self.params:
                timeout = self.cache_count_all_timeout
            string = self.cache_request(func)
            self.cache.set(string, value, timeout)

    def cache_request(self, func):
        query = self.query.copy()
        query['limit'] = query['offset'] = 0
        params = tuple(sorted(query.items()))
        query = tuple(sorted(query.items()))
        cache_string = str(query) + str(params) + func.__name__
        return cache_string

    def run(self, func):
        if self.cache:
            string = self.cache_request(func)
            return self.cache.get_or_set(string, func(self.params, **self.query), self.cache_timeout)
        return func(self.params, **self.query)

    def rowcount(self):
        return len(self.results)

    def start(self):
        self.enter_func()

    def close(self, **kwargs):
        self.exit_func(**kwargs)