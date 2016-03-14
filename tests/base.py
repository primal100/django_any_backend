import pycountry
from any_backend.testcases import CompareWithSQLTestCase

"""def populate():
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
            subdivision_model.objects.bulk_create(subdivision_instances)"""

class PickleDBTest(CompareWithSQLTestCase):
    fixtures = ["chinookdata.default.json", "chinookdata.pickle_db.json"]
    def setUp(self):
        self.override_settings = {'DEBUG': True}