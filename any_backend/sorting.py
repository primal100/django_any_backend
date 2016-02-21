import operator

class OrderBy(object):
    def __init__(self, field_name, reverse=False):
        self.field_name = field_name
        self.reverse = reverse

    def apply(self, objects):
        return sorted(objects, key=lambda k: k[self.field_name], reverse=self.reverse)


class OrderingList(list):

    def apply(self, objects, is_dict, exclude_columns=None):
        for column in exclude_columns:
            self.remove(column)
        args = []
        for column in self:
            args.append(column.field_name)
        reverse = self[0].reverse
        if is_dict:
            return sorted(objects, key=operator.itemgetter(args), reverse=reverse)
        else:
            return sorted(objects, key=operator.attrgetter(args), reverse=reverse)

    def to_dict(self):
        orderings = []
        for order in self:
            orderings.append(order.field_name)
        reverse = self[0].reverse
        return {'orderby': orderings, 'reverse': reverse}