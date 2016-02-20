from django.contrib.admin import ModelAdmin as MA
from any_backend.paginators import APIPaginator

class ModelAdmin(MA):
    paginator = APIPaginator
    show_full_result_count = False

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page, request=request)

