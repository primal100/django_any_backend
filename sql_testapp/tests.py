from django.test import TestCase
from django.db.models import ObjectDoesNotExist
from models import Country, Subdivision
from django.conf import settings
import os
from any_backend.utils import make_dict_from_obj, toDicts
import pycountry

class PickleTest(TestCase):

    def setUp(self):
        country_codes = []
        for country in list(pycountry.countries)[0:30]:
            model = Country(name=country.name, alpha2=country.alpha2, numeric=country.numeric)
            model.save()
            country_codes.append(country.alpha2)
        for subdivision in list(pycountry.subdivisions)[0:600]:
            if subdivision.country_code in country_codes:
                country = Country.objects.get(alpha2=subdivision.country_code)
                model = Subdivision(name=subdivision.name, code=subdivision.code, country=country, type=subdivision.type)
                model.save()

    def test_all(self):
        equalto = Country.objects.all()
        self.assertEqual(Country.objects.all(), equalto)

    def test_get(self):
        equalto = ''
        self.assertEqual(make_dict_from_obj(Country.objects.get(id='AU')), equalto)

    def test_first(self):
        equalto = ''
        self.assertEqual(make_dict_from_obj(Country.objects.all().order_by('name').first()), equalto)

    def test_last(self):
        equalto = ''
        self.assertEqual(make_dict_from_obj(Country.objects.filter(continent='Europe').order_by('id').last()), equalto)

    def test_filter(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.filter(continent='Africa', language='Asia')), equalto)

    def test_ordering(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.all().order_by('-continent', 'language', 'name')), equalto)

    def test_distinct(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.all().distinct('continent', 'language')), equalto)

    def test_pagination(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.all().order_by('-name'))[5:10], equalto)

    def test_count(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.all().count()), equalto)

    def test_count_with_filter(self):
        equalto = 2
        self.assertEqual(toDicts(Country.objects.filter(continent=2)), equalto)

    def test_create(self):
        equalto = ''
        kwargs = dict(name='USA', continent='North America', capital='Washington',
                                   language='English')
        self.assertRaises(
            Country.objects.filter(**kwargs).get(), ObjectDoesNotExist)
        usa = Country(**kwargs)
        equalto = ''
        self.assertEqual(usa.save(), equalto)
        equalto = ''
        self.assertEqual(make_dict_from_obj(
            Country.objects.filter(**kwargs).get()), equalto)

    def test_update(self):
        equalto = ''
        filter1 = dict(name='Ireland')
        filter2 = dict(name='Scotland')
        self.assertRaises(
            Country.objects.filter(**filter2).get(), ObjectDoesNotExist)
        scotland =  Country.objects.filter(**filter1)
        scotland.name = 'Scotland'
        equalto = ''
        self.assertEqual(scotland.save(), equalto)
        equalto = ''
        self.assertEqual(make_dict_from_obj(Country.objects.filter(**filter2).get()), equalto)

    def test_delete(self):
        equalto = ''
        filter = dict(continent='Asia')
        self.assertEqual(make_dict_from_obj(
            Country.objects.filter(**filter)), equalto)
        equalto = ''
        self.assertEqual(Country.objects.filter(**filter).delete(), equalto)
        self.assertRaises(make_dict_from_obj(
        Country.objects.filter(**filter).get()), ObjectDoesNotExist)