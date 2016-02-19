class OrderBy(object):
    def __init__(self, field_name, reverse=False):
        self.field_name = field_name
        self.reverse = reverse

class OrderingList(object):
    def __init__(self, order_by):
        self.columns = []
        for ordering in order_by:
            self.columns.append(ordering)

    def get(self, obj, is_dict, sensitive):
            if is_dict:
                value = obj[self.field_name]
            else:
                value = getattr(obj, self.field_name)
            if sensitive:
                return value
            else:
                return value.lower()

    def sort_objects(self, objs, exclude_columns=None):
        for column in exclude_columns:
            self.columns.remove(column)
        for column in self.columns:
            objs = sorted(objs, key=lambda k: k['column'], reverse=column.reverse)