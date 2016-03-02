from any_backend.testcases import CompareWithSQLTestCase
from models import Country, Subdivision
from sql_testapp.models import Country as SQLCountry, Subdivision as SQLSubdivision
import pycountry

class PickleTest(CompareWithSQLTestCase):

    def setUp(self):
        self.models = ((SQLCountry, SQLSubdivision), (Country, Subdivision))
        for models in self.models:
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

    def with_cache(self, func, *args, **kwargs):
        func(*args, **kwargs)
        with self._overridden_settings():
            func(*args, **kwargs)
            
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
        self.assertQuerysetsEqual(sql_result, nondb_result)
        nondb_qs = Country.objects.filter(name='Ireland')
        self.assertRaises(Country.DoesNotExist, nondb_qs.get)

    @with_cache
    def test_delete_subdivision(self):
        sql_result = self.first_with_time(SQLSubdivision.objects.filter(type='parish'))
        nondb_result = self.first_with_time(Subdivision.objects.filter(type='parish'))
        self.assertQuerysetsEqual(sql_result, nondb_result)
        nondb_qs = Subdivision.objects.filter(type='parish')
        self.assertRaises(Subdivision.DoesNotExist, nondb_qs.get)