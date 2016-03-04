import operator
from utils import getvalue

class OrderBy(object):
    def __init__(self, field_name, reverse=False):
        self.field_name = field_name
        self.reverse = reverse

    def apply(self, objects):
        return sorted(objects, key=lambda k: getvalue(k, self.field_name), reverse=self.reverse)

class OrderingList(list):

    def __repr__(self):
        string = 'Ordering='
        for column in self:
            string += column + ';'
        return string

    def apply(self, objects,  exclude_columns=()):
        for column in exclude_columns:
            self.remove(column)
        args, reverse = self.to_list()
        if objects:
            if hasattr(objects[0], '__getitem__'):
                return sorted(objects, key=operator.itemgetter(*args), reverse=reverse)
            else:
                return sorted(objects, key=operator.attrgetter(*args), reverse=reverse)
        else:
            return objects

    def to_list(self):
        ordering = []
        reverse = False
        reverse_set = False
        for column in self:
            if column.startswith('-'):
                name = column.split('-')[1]
                ordering.append(name)
                if not reverse_set:
                    reverse = True
            else:
                ordering.append(column)
                if not reverse_set:
                    reverse = False
            reverse_set = True
        return ordering, reverse

    def to_dicts(self):
        ordering = []
        for column in self:
            if column.startswith('-'):
                name = column.split('-')[1]
                ordering.append({'column': name, 'reverse': True})
            else:
                ordering.append({'column': column, 'reverse': False})
        return ordering