from collections import OrderedDict

class Connection(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def create(self, params, **kwargs):
        """

        :param params:
        :param kwargs:
        :return: id of object successfully created
        """

        raise NotImplementedError('You must implement a create function in your connection class')

    def list(self, params, **kwargs):
        raise NotImplementedError('You must implement a list function in your connection class')

    def delete(self, params, **kwargs):
        raise NotImplementedError('You must implement a delete function in your connection class')

    def update(self, params, **kwargs):
        raise NotImplementedError('You must implement an update function in your connection class')

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
            kwargs['results'] = [obj]
            ids.append(self.create(params, **kwargs))
        return ids

    def delete_bulk(self, params, **kwargs):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully deleted
        """
        ids = []
        objects = kwargs.pop('results')
        for obj in objects:
            kwargs['results'] = [obj]
            ids.append(self.delete(params, **kwargs))
        return ids

    def update_bulk(self, params, **kwargs):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully updated
        """
        ids = []
        objects = kwargs.pop('results')
        for obj in objects:
            kwargs['results'] = [obj]
            ids.append(self.update(params, **kwargs))
        return ids

    def enter(self):
        pass

    def exit(self, exc_type=None, exc_val=None, exc_tb=None):
        pass

    def convert_dict(self, dict, model):
        values = []
        for field in model._meta.fields:
            value = dict[field]
            if type(value) == dict:
                value = self.convert_dict(value, field.to)
            values.append(dict[field])
        as_tuple = tuple(values)
        return as_tuple

    def convert_dicts_to_tuples(self, dicts):
        tuples = []
        for dict in dicts:
            tuples.append(self.convert_dict(dict))
        return tuples

    def convert_object(self, dict, model):
        values = []
        for field in model._meta.fields:
            value = dict[field]
            if type(value) == dict:
                value = self.convert_object(value, field.to)
            values.append(dict[field])
        as_tuple = tuple(values)
        return as_tuple

    def convert_dicts_to_tuples(self, objs):
        tuples = []
        for dict in dicts:
            tuples.append(self.convert_object(obj))
        return tuples