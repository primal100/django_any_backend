import operator
from utils import getvalue

class OrderBy(object):
    def __init__(self, field_name, reverse=False):
        self.field_name = field_name
        self.reverse = reverse

    def apply(self, objects):
        return sorted(objects, key=lambda k: getvalue(k, self.field_name), reverse=self.reverse)

class OrderingList(list):

    def set_reverse(self, standard_ordering):
        self.reverse_ordering = not standard_ordering

    def __repr__(self):
        string = 'Ordering=%s' % (self.reverse_ordering)
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
        reverse = self.reverse_ordering
        for column in self:
            if column.startswith('-'):
                name = column.split('-')[1]
                ordering.append(name)
            else:
                ordering.append(column)
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