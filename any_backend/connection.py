class Connection(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def list(self, params, **kwargs):
        raise NotImplementedError('You must implement a list function in your connection class')

    def setup(self):
        pass

    def get(self, params, **kwargs):
        return self.list(params, **kwargs)[0]

    def count(self, params, **kwargs):
        return len(self.list(params, **kwargs))

