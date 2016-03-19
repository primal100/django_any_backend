import pycountry
from any_backend.testcases import AnyBackendTestCase

class PickleDBTest(AnyBackendTestCase):
    fixtures = ["tracks.default.json", "tracks.pickle_db.json"]

    #def setUp(self):
    #    #self.override_settings = {'DEBUG': True}