from django.core.paginator import Paginator
from django.contrib.admin.views.main import PAGE_VAR

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