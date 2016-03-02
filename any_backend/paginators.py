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
        self.this_page = self.page(page_num + 1)

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            try:
                #self.this_page = self.page(self.page_num)
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list). Will return the length of requested page only.
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

class BackendPaginator(object):
    def __init__(self, with_limits, low_mark, high_mark, no_limit_value):
        self.paginated = with_limits
        if not low_mark and not high_mark:
            self.paginated = False
        if self.paginated:
            self.paginate(low_mark, high_mark, no_limit_value)

    def paginate(self, low_mark, high_mark, no_limit_value):
        self.low_mark = low_mark or 0
        self.high_mark = high_mark
        if not self.high_mark:
                self.high_mark = no_limit_value
        self.page_size = self.high_mark - self.low_mark + 1
        self.page_num = ceil(self.low_mark / self.page_size) + 1

    def update(self, pos, size):
        if size:
            low_mark = self.low_mark =+ pos
            high_mark = low_mark + size - 1
            self.paginated = True
            self.paginate(low_mark, high_mark, None)

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

    def as_dict(self):
        return {'low': self.low_mark, 'high': self.high_mark}