from django.core.paginator import Paginator
from django.contrib.admin.views.main import PAGE_VAR
from math import ceil

class APIPaginator(Paginator):

    def __init__(self, object_list, per_page, orphans=0,
                 allow_empty_first_page=True, request=None, page_num=None):
        super(APIPaginator, self).__init__(object_list, per_page, orphans=orphans,
                                           allow_empty_first_page=allow_empty_first_page)
        self.page_num = None
        if page_num or request:
            self.page_num = page_num or request.GET.get(PAGE_VAR, None)
        self.this_page = None

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            try:
                self.this_page = self.page(self.page_num)
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list). Will return the length of requested page only.
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def page(self, number):
        if getattr(self.this_page, number, None) != number:
             self.this_page = super(APIPaginator, self).page(number)
        return self.this_page

class BackendPaginator(object):
    def __init__(self, with_limits, low_mark, high_mark, no_limit_value):
        self.paginated = with_limits
        if self.paginated:
            self.low_mark = low_mark
            self.high_mark = high_mark
            if self.high_mark is not None:
                self.limit = self.high_mark - self.low_mark
            else:
                self.limit = None
            if self.low_mark:
                if self.high_mark is None:
                    val = no_limit_value
                    if val:
                        self.limit = val
            self.offset = self.low_mark
            self.page_size = self.offset - self.limit
            self.page_num = ceil(self.limit / self.page_size) + 1

    def apply(self, objects):
        if self.paginated:
            return objects[self.low_mark:self.high_mark]
        else:
            return objects

    def as_dict(self):
        return {'low': self.low_mark, 'high': self.high_mark}