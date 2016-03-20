from math import ceil

class BackendPaginator(object):
    def __init__(self, with_limits, low_mark, high_mark, no_limit_value):
        self.paginated = with_limits
        self.low_mark = low_mark or 0
        self.high_mark = high_mark
        if not self.high_mark:
                self.high_mark = no_limit_value
        if not self.low_mark and not self.high_mark:
            self.paginated = False
        if self.paginated:
            self.paginate()

    def paginate(self):
        self.page_size = self.high_mark - self.low_mark
        self.page_num = ceil(self.low_mark / self.page_size) + 1

    def update(self, pos, size):
        if size:
            self.low_mark = self.low_mark =+ pos
            self.high_mark = self.low_mark + size
            self.paginated = True
            self.paginate()

    def apply(self, objects):
        if self.paginated:
            if len(objects) > self.high_mark:
                return objects[self.low_mark:self.high_mark]
            elif len(objects) > self.low_mark:
                return objects[self.low_mark:len(objects)]
            else:
                return []
        else:
            return objects

    def __repr__(self):
        return 'BackendPaginator=' + str(self.low_mark) + '-' + str(self.high_mark)

    def to_dict(self):
        if self.paginated:
            return {'low': self.low_mark, 'high': self.high_mark}
        return {}