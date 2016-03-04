from utils import getvalue

class DistinctFields(list):

    def __repr__(self):
        string = 'distinct='
        for distinct in sorted(self):
            string += distinct.field.column + ';'
        return string

    def apply(self, objects):
        strings = []
        for object in objects:
            string = ''
            for distinct in self:
                string += getvalue(object, distinct.field, returnIfNone='')
                if string in strings:
                    objects.remove(object)
                else:
                    strings.append(string)
        return objects

