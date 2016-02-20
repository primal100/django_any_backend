from django.test import TestCase
from models import Country
from django.conf import settings
import os

countries = [{'id': 0, 'name': 'Ireland', 'capital': 'Dublin', 'continent': 'Europe'},
               {'id': 1, 'name': 'Botswana', 'capital': 'Gaborone', 'continent': 'Africa'},
               {'id': 2, 'name': 'El Salvador', 'capital': 'San Salvador', 'continent': 'North America'},
               {'id': 3, 'name': 'Japan', 'capital': 'Tokyo', 'continent': 'Asia'},
               {'id': 4, 'name': 'Brazil', 'capital': 'Brasilia', 'continent': 'South America'},
               {'id': 5, 'name': 'New Zealand', 'capital': 'Auckland', 'continent': 'Australia'},
               {'id': 6, 'name': 'Oman', 'capital': 'Muscat', 'continent': 'Asia'},
               {'id': 7, 'name': 'Egypt', 'capital': 'Cairo', 'continent': 'Africa'},
               {'id': 8, 'name': 'Sweden', 'capital': 'Stockholm', 'continent': 'Europe'}]

class PickleTest(TestCase):
    def setUp(self):
        database = settings['DATABASES']['pickle_db']
        if not os.path.isfile(database['FILENAME']):
            for country in countries:
                model = Country(name=country['name'], capital=country['capital'], continent=country['continent'])
                model.save()

class CursorTest(TestCase):
    """
    Tests any_backend.backend.compiler and any_backend.backend.cursor
    """
    pass


class ConnectionTest(TestCase):
    """
    Tests any_backend.backend.connection and any_backend.backend.operations
    """
    pass

class ListTest(TestCase):
    """
    Tests any_backend.filters, any_backend.distinct, any_backend.sorting any_backend.paginators and any_backend.backends.client.list
    """
    pass

class WriteTest(TestCase):
    """
    Tests any_backend.updaet_with, any_backend.backends.client.delete, any_backend.backends.client.create and any_backend.backends.client.update

    """

class DBRouterTest(TestCase):
    """
    Tests any_backend.routers

    """

class ModelAdminTest(TestCase):
    """
    Tests any_backend.paginators and any_backend.admin
    """