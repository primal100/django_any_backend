from django.test import TestCase
from django.db.models import ObjectDoesNotExist
from models import Country
from django.conf import settings
import os
from any_backend.utils import make_dict_from_obj, toDicts

countries = [{'id': 0, 'name': 'Ireland', 'capital': 'Dublin', 'continent': 'Europe', 'language': 'English'},
               {'id': 1, 'name': 'Botswana', 'capital': 'Gaborone', 'continent': 'Africa', 'language': 'English'},
               {'id': 2, 'name': 'El Salvador', 'capital': 'San Salvador', 'continent': 'North America', 'language': 'Spanish'},
               {'id': 3, 'name': 'Japan', 'capital': 'Tokyo', 'continent': 'Asia', 'language': 'Japanese'},
               {'id': 4, 'name': 'Brazil', 'capital': 'Brasilia', 'continent': 'South America', 'language': 'Portuguese'},
               {'id': 5, 'name': 'New Zealand', 'capital': 'Auckland', 'continent': 'Australia', 'language': 'English'},
               {'id': 6, 'name': 'Oman', 'capital': 'Muscat', 'continent': 'Asia', 'language': 'Arabic'},
               {'id': 7, 'name': 'Egypt', 'capital': 'Cairo', 'continent': 'Africa', 'language': 'Arabic'},
               {'id': 8, 'name': 'Sweden', 'capital': 'Stockholm', 'continent': 'Europe', 'language': 'Swedish'}]

class PickleTest(TestCase):
    def setUp(self):
        database = settings['DATABASES']['pickle_db']
        filename = os.path.isfile(database['FILENAME'])
        if os.path.isfile(database['FILENAME']):
            os.remove(filename)
        for country in countries:
            model = Country(name=country['name'], capital=country['capital'], continent=country['continent'])
            model.save()

    def test_all(self):
        equalto = ''
        self.assertEqual(toDicts(Country.objects.all()), equalto)

    def test_get(self):
        equalto = ''
        self.assertEqual(make_dict_from_obj(Country.objects.get(id=1)), equalto)

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
        equalto = len(countries)
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