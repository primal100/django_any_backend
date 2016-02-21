from utils import getvalue

class DistinctFields(list):

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

