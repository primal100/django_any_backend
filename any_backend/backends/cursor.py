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
        if 'CREATE TABLE' in query:
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
            cache = db_config.get('CACHE', None)
            if cache:
                cache_name = cache['NAME']
                self.cache = caches[cache_name]
                self.cache_timeout = cache.get('TIMEOUT', 60)
                self.cache_count_all_timeout = cache.get('COUNT_ALL_TIMEOUT', self.cache_timeout)
            else:
                self.cache = None
            self.query = query
            self.params = params
            self.pos = 0
            if self.immediate_execute:
                if self.model._meta.db_table == 'django_migrations':
                    self.results = []
                else:
                    if 'is_get_pks' in self.query.keys():
                        self.query = {}
                    self.results = self.func(self.model, self.params, **self.query)
                    self.results = self.conversion_func(self.results, self.fieldnames)
                    if self.cache:
                        self.cache.clear()
            elif self.model._meta.db_table != 'django_migrations':
                self.results = []
                if 'paginator' in self.query:
                    self.paginated = self.query['paginator'].paginated
                    if self.paginated:
                        self.page_size = self.query['paginator'].page_size
                self.size = self.model.max_per_request
                self.full_request_size = None
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
        if self.results:
            result = self.conversion_func(self.results, self.fieldnames)[self.pos]
        else:
            result = []
        self.pos += 1
        return result

    def fetchmany(self, size=0):
        if self.immediate_execute:
            tuples = self.conversion_func(self.results, self.fieldnames)
            return tuples
        elif self.model._meta.db_table == 'django_migrations':
            self.results, self.pre_paginate_count = [], 0
            return self.results
        else:
            if not self.full_request_size or self.pos <= self.full_request_size:
                self.query['paginator'].update(self.pos, self.size)
                if self.cache:
                    self.results = self.cache_get(default=[])
                    self.pre_paginate_count = self.cache_get(default=())
                    if self.results:
                        return self.results
                self.results, self.pre_paginate_count = self.func(self.model, self.params, **self.query)
                self.results = self.conversion_func(self.results, self.fieldnames)
                self.full_request_size = self.page_size if self.paginated else self.pre_paginate_count
                if self.size:
                    self.pos += size
                else:
                    self.pos += self.pre_paginate_count + 1
                self.pre_paginate_count = (self.pre_paginate_count,)
                self.cache_set(self.results)
                self.cache_set(self.pre_paginate_count)
                if self.count:
                    return self.pre_paginate_count
                else:
                    return self.results
            else:
                return []


    def fetchall(self):
        return list(self.fetchmany())

    def cache_get(self, default=None):
        if self.cache:
            string = self.cache_key(self.func)
            return self.cache.get(string, default=default)
        return None

    def cache_set(self, value):
        if self.cache:
            if self.count and not self.params:
                timeout = self.cache_count_all_timeout
            else:
                timeout = self.cache_timeout
            string = self.cache_key(self.func)
            self.cache.set(string, value, timeout)

    @staticmethod
    def list_to_string(key, newlist):
        newlist = sorted(newlist)
        string = key + ':'
        for l in newlist:
            string += str(l) + '-'
        return string

    def dict_to_string(self, key, dictionary):
        newlist = []
        for k, v in dictionary.iteritems():
            newlist.append(str(k) + ':' + str(v))
        string = self.list_to_string(key, newlist)
        return string

    def cache_key(self, func):
        model_name = self.model._meta.model_name
        params = self.dict_to_string('params', self.params.to_dict())
        distinct = self.list_to_string('distinct', self.query['distinct'])
        out_cols = self.list_to_string('fieldnames', self.fieldnames)
        if 'paginator' in self.query:
            paginator = sorted(self.query['paginator'].to_dict())
        else:
            paginator = {}
        paginator = self.list_to_string('paginator', paginator)
        if 'order_by' in self.query:
            order_by = sorted(self.query['order_by'])
        else:
            order_by = {}
        order_by = self.list_to_string('order_by', paginator)
        cache_string = model_name + params + distinct + out_cols + paginator + self.func.__name__
        return cache_string

    def start(self):
        if self.enter_func:
            self.enter_func()

    def close(self, **kwargs):
        if self.exit_func:
            self.exit_func(**kwargs)