class UpdateParams(dict):

    def apply(self, object):
        for k, v in self.iteritems():
            object[k] = v
        return object