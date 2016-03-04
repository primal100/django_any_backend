from django.core.paginator import Paginator
from django.contrib.admin.views.main import PAGE_VAR
from math import ceil

class APIPaginator(Paginator):

    def __init__(self, object_list, per_page, orphans=0,
                 allow_empty_first_page=True, request=None, page_num=None):
        super(APIPaginator, self).__init__(object_list, per_page, orphans=orphans,
                                           allow_empty_first_page=allow_empty_first_page)
        page_num = page_num
        if not page_num and request:
            page_num = int(request.GET.get(PAGE_VAR, 0))
        bottom = (page_num) * self.per_page
        top = bottom + self.per_page
        self.page_object_list = list(self.object_list[bottom:top])

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.page_object_list, number, self)

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
        self.page_size = self.high_mark - self.low_mark + 1
        self.page_num = ceil(self.low_mark / self.page_size) + 1

    def update(self, pos, size):
        if size:
            self.low_mark = self.low_mark =+ pos
            self.high_mark = self.low_mark + size - 1
            self.paginated = True
            self.paginate()

    def apply(self, objects):
        if self.paginated:
            if len(objects) > self.high_mark:
                return objects[self.low_mark:self.high_mark + 1]
            elif len(objects) > self.low_mark:
                return objects[self.low_mark:len(objects) + 1]
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