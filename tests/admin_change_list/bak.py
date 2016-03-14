from tests.base import PickleDBTest
from django.test.client import RequestFactory
from testapp.admin import CountryAdmin
from testapp.admin import CountryAdmin as SQLCountryAdmin
from sql_testapp.models import Country as SQLCountry
from testapp.models import Country
from django import te

class AdminTest(PickleDBTest):
    def setUp(self):
        self.model_admins = (SQLCountryAdmin(SQLCountry, ''), CountryAdmin(Country, ''))

    def test_change_list_results(self):
        list_per_page = 50
        factory = RequestFactory()
        request = factory.get('admin/testapp/country?p=1')
        page_num = int(request.GET.get('p', 0))
        result_count = []
        full_result_count = []
        result_list = []
        with self.settings(**self.override_settings):
            for i, model_admin in enumerate(self.model_admins):
                root_queryset = model_admin.model.objects.all()
                queryset = root_queryset.filter(name__contains='land')
                paginator = model_admin.get_paginator(request, queryset, list_per_page)
                result_count[i] = paginator.count
                full_result_count[i] = root_queryset.count()
                result_list[i] = paginator.page(page_num + 1)
            self.assertEqual(result_count[0], result_count[1])
            self.assertEqual(full_result_count[0], full_result_count[1])
            self.assertQuerysetsEqual(result_list[0], result_list[1])