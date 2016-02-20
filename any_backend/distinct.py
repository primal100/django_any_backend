class DistinctFields(list):

    def apply(self, objects):
        strings = []
        for object in objects:
            string = ''
            for distinct in self:
                string += distinct.field
                if string in strings:
                    objects.remove(object)
                else:
                    strings.append(string)
        return objects

