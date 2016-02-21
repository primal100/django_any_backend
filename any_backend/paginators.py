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
    def __init__(self, with_limits, offset, limit, no_limit_value):
        self.paginated = with_limits
        if self.paginated:
            self.offset = offset or 0
            self.limit = limit
            if self.offset:
                if self.limit is None:
                    val = no_limit_value
                    if val:
                        self.limit = val
            self.update_range(self.offset, self.limit)

    def update_range(self, offset, limit):
        self.offset = offset
        self.limit = limit
        self.page_size = self.limit - self.offset
        if self.page_size:
            self.paginated = True
            self.page_num = ceil(self.limit / self.page_size) + 1
        else:
            self.paginated = False
            self.page_num = 1

    def apply(self, objects):
        if self.paginated:
            if len(objects) > self.limit:
                return objects[self.offset:self.limit]
            elif len(objects) > self.offset:
                return objects[self.offset:len(objects)]
            else:
                return []
        else:
            return objects

    def as_dict(self):
        return {'low': self.offset, 'high': self.limit}