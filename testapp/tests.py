from any_backend.testcases import CompareWithSQLTestCase
from models import Country, Subdivision
from sql_testapp.models import Country as SQLCountry, Subdivision as SQLSubdivision
from testapp.admin import CountryAdmin
from sql_testapp.admin import CountryAdmin as SQLCountryAdmin
from django.test.client import RequestFactory
import pycountry

def populate():
    models_list = ((SQLCountry, SQLSubdivision), (Country, Subdivision))
    for models in models_list:
        country_model = models[0]
        if len(country_model.objects.all()) == 0:
            country_instances = []
            for country in list(pycountry.countries)[0:30]:
                instance = country_model(name=country.name, alpha2=country.alpha2, numeric=country.numeric)
                country_instances.append(instance)
            country_model.objects.bulk_create(country_instances)
            subdivision_model = models[1]
            subdivision_instances = []
            for subdivision in list(pycountry.subdivisions):
                if any(subdivision.country_code == x.alpha2 for x in country_instances):
                    country = country_model.objects.filter(alpha2=subdivision.country_code).get()
                    instance = subdivision_model(name=subdivision.name, code=subdivision.code, country=country, type=subdivision.type)
                    subdivision_instances.append(instance)
            subdivision_model.objects.bulk_create(subdivision_instances)

class PickleTest(CompareWithSQLTestCase):

    def setUp(self):
        populate()

    def test_countries_all(self):
        sql_queryset = SQLCountry.objects.all().order_by('alpha2')
        nondb_queryset = Country.objects.all().order_by('alpha2')
        self.breakdown_queryset(nondb_queryset)
        self.assertQuerysetsEqual(sql_queryset, nondb_queryset)

    def test_subdivisions_all(self):
        sql_queryset = SQLSubdivision.objects.all().order_by('code')
        nondb_queryset = Subdivision.objects.all().order_by('code')
        self.breakdown_queryset(nondb_queryset)
        self.assertQuerysetsEqual(sql_queryset, nondb_queryset)

    def test_count(self):
        self.assertEqual(self.count_with_time(SQLCountry.objects.all()), 30)
        self.assertEqual(self.count_with_time(Country.objects.all()), 30)

    def test_get(self):
        sql_result = self.get_with_time(SQLSubdivision.objects.filter(name='Armavir'))
        nondb_result = self.get_with_time(Subdivision.objects.filter(name='Armavir'))
        self.assertEqual(str(sql_result), str(nondb_result))

    def test_last(self):
        sql_result = self.last_with_time(SQLSubdivision.objects.filter(code='AU').order_by('code'))
        nondb_result = self.last_with_time(Subdivision.objects.filter(code='AU').order_by('code'))
        self.assertQuerysetsEqual(sql_result, nondb_result)

    def test_first(self):
        sql_result = self.first_with_time(SQLSubdivision.objects.filter(type='parish').order_by('code'))
        nondb_result = self.first_with_time(Subdivision.objects.filter(type='parish').order_by('code'))
        self.assertQuerysetsEqual(sql_result, nondb_result)

    def test_save(self):
        pass

    def test_delete_county(self):
        sql_result = self.first_with_time(SQLCountry.objects.filter(name='Ireland'))
        nondb_result = self.first_with_time(Country.objects.filter(name='Ireland'))
        self.assertEqual(sql_result, nondb_result)
        nondb_qs = Country.objects.filter(name='Ireland')
        self.assertRaises(Country.DoesNotExist, nondb_qs.get)

    def test_delete_subdivision(self):
        sql_result = self.first_with_time(SQLSubdivision.objects.filter(type='parish'))
        nondb_result = self.first_with_time(Subdivision.objects.filter(type='parish'))
        self.assertQuerysetsEqual(sql_result, nondb_result)
        nondb_qs = Subdivision.objects.filter(type='parish')
        self.assertRaises(Subdivision.DoesNotExist, nondb_qs.get)

class AdminTest(CompareWithSQLTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_admin = CountryAdmin(Country, '')
        self.root_queryset = self.model_admin.model.objects.all()
        self.queryset = self.root_queryset.filter(name__countains='land')
        self.sql_model_admin = SQLCountryAdmin(SQLCountry, '')
        self.sql_root_queryset = self.sql_model_admin.model.objects.all()
        self.sql_queryset = self.sql_root_queryset.filter(name__countains='land')
        self.list_per_page = 50

    def test_change_list(self):
        request = self.factory.get('admin/testapp/country?p=1')
        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)
        sql_paginator = self.sql_model_admin.get_paginator(request, self.queryset, self.list_per_page)
        page_num = int(request.GET.get('p', 0))
        result_count = self.prop_with_time(paginator, 'count', 'nondb_paginator.count')
        full_result_count = self.count_with_time(self.root_queryset)
        table = self.sql_model_admin.model._meta.db_table
        result_list = self.prop_with_time(table, 'result_list', self.run_with_time(table, paginator.page, page_num + 1),
                                          'object_list')
        sql_result_count = self.prop_with_time(sql_paginator, 'count', 'sql_paginator.count')
        sql_full_result_count = self.count_with_time(self.sql_root_queryset)
        sql_table = self.sql_model_admin.model._meta.db_table
        sql_result_list = self.prop_with_time(sql_table, 'result_list',
                                              self.run_with_time(sql_table, sql_paginator.page, page_num + 1),
                                              'object_list')
        self.assertEqual(result_count, sql_result_count)
        self.assertEqual(full_result_count, sql_full_result_count)
        self.assertEqual(result_list, sql_result_list)