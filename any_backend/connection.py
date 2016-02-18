class Connection(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def create(self, params, **kwargs):
        """

        :param params:
        :param kwargs:
        :return: id of last object created
        """

        raise NotImplementedError('You must implement a create function in your connection class')

    def list(self, params, **kwargs):
        raise NotImplementedError('You must implement a list function in your connection class')

    def delete(self, params, **kwargs):
        raise NotImplementedError('You must implement a delete function in your connection class')

    def setup(self):
        pass

    def get(self, params, **kwargs):
        return self.list(params, **kwargs)[0]

    def count(self, params, **kwargs):
        return len(self.list(params, **kwargs))

    def create_bulk(self, params, **kwargs):
        ids = []
        objects = kwargs.pop('objects')
        for obj in objects:
            kwargs['objects'] = [obj]
            ids.append(self.create(params, **kwargs))
        return ids

    def delete_bulk(self, params, **kwargs):
        ids = []
        objects = kwargs.pop('objects')
        for obj in objects:
            kwargs['objects'] = [obj]
            ids.append(self.delete(params, **kwargs))
        return ids

    def enter(self):
        pass

    def exit(self, exc_type=None, exc_val=None, exc_tb=None):
        pass

