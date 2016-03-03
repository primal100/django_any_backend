from utils import getvalue

class Filters(list):
    def apply(self, objects):
        for filter in self:
            objects = filter.apply(objects)
        return objects

    def to_dict(self):
        dictionary = {}
        for filter in self:
            if filter.operator == 'exact':
                dictionary[filter.field_name] = filter.value
            elif filter.operator == 'iexact':
                dictionary[filter.field_name] = filter.value.lower()
        return dictionary

class Filter(object):
    def __init__(self, field, operator, value):
        self.field = field
        self.field_name = field.column
        self.field_type = field.get_internal_type()
        self.operator = operator
        self.value = value

    def get(self, obj, sensitive):

        value = getvalue(obj, self.field_name, returnIfNone='')
        if not sensitive:
            return value.lower()
        return value

    def apply(self, objlist):
        if self.operator == 'exact':
            return [d for d in objlist if self.get(d, True) == self.value]
        elif self.operator == 'iexact':
            return [d for d in objlist if self.get(d, False) == self.value.lower()]
        elif self.operator == 'contains':
            return [d for d in objlist if self.value in self.get(d, True)]
        elif self.operator == 'icontains':
            return [d for d in objlist if self.value.lower() in self.get(d, False)]
        elif self.operator == 'in':
            return [d for d in objlist if self.get(d, True) in self.value]
        elif self.operator == 'gt':
            return [d for d in objlist if self.get(d, True) > self.value]
        elif self.operator == 'gte':
            return [d for d in objlist if self.get(d, True) >= self.value]
        elif self.operator == 'lt':
            return [d for d in objlist if self.get(d, True) < self.value]
        elif self.operator == 'lte':
            return [d for d in objlist if self.get(d, True) <= self.value]
        elif self.operator == 'startswith':
            return [d for d in objlist if self.get(d, True).startswith(self.value)]
        elif self.operator == 'istartswith':
            return [d for d in objlist if self.get(d, False).lower().startswith(self.value.lower())]
        elif self.operator == 'endswith':
            return [d for d in objlist if self.get(d, True).endswith(self.value)]
        elif self.operator == 'iendswith':
            return [d for d in objlist if self.get(d, False).endswith(self.value.lower())]
        else:
            raise NotImplementedError('Operator ' + self.operator + ' not supported.')