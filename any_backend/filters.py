class Filters(list):
    def apply(self, objects, is_dict):
        for filter in self:
            objects = filter.apply(objects, is_dict)
            return objects

    def as_dict(self):
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
        self.field_name = field.name
        self.field_type = field.get_internal_type()
        self.operator = operator
        self.value = value

    def get(self, obj, is_dict, sensitive):
        if is_dict:
            value = obj[self.field_name]
        else:
            value = getattr(obj, self.field_name)
        if sensitive:
            return value
        else:
            return value.lower()

    def apply(self, objlist, is_dict):
        if self.operator == 'exact':
            return [d for d in objlist if self.get(d, is_dict, True) == self.value]
        elif self.operator == 'iexact':
            return [d for d in objlist if self.get(d, is_dict, False) == self.value.lower()]
        elif self.operator == 'contains':
            return [d for d in objlist if self.value in self.get(d, is_dict, True)]
        elif self.operator == 'icontains':
            return [d for d in objlist if self.value.lower() in self.get(d, is_dict, False)]
        elif self.operator == 'in':
            return [d for d in objlist if self.get(d, is_dict, True) in self.value]
        elif self.operator == 'gt':
            return [d for d in objlist if self.get(d, is_dict, True) > self.value]
        elif self.operator == 'gte':
            return [d for d in objlist if self.get(d, is_dict, True) >= self.value]
        elif self.operator == 'lt':
            return [d for d in objlist if self.get(d, is_dict, True) < self.value]
        elif self.operator == 'lte':
            return [d for d in objlist if self.get(d, is_dict, True) <= self.value]
        elif self.operator == 'startswith':
            return [d for d in objlist if self.get(d, is_dict, True).startswith(self.value)]
        elif self.operator == 'istartswith':
            return [d for d in objlist if self.get(d, is_dict, False).lower().starswith(self.value.lower())]
        elif self.operator == 'endswith':
            return [d for d in objlist if self.get(d, is_dict, True).endswith(self.value)]
        elif self.operator == 'iendswith':
            return [d for d in objlist if self.get(d, is_dict, False).endswith(self.value.lower())]
        else:
            raise NotImplementedError('Operator ' + self.operator + ' not supported.')