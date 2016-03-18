import logging

logger = logging.getLogger('django')

class CursorRequest(object):

    def __init__(self, func, key, *args, **kwargs):
        self.func = func
        self.key = key
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.key)

    def __str__(self):
        return self.key

class Cursor(object):

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute(self, sql):
        self.results = sql.func(*sql.args, **sql.kwargs)
        return self.results

    @property
    def rowcount(self):
        if type(self.results) == int:
            return self.results
        return len(self.results)

    @property
    def lastrowid(self):
        return self.results[-1]

    def close(self):
        pass