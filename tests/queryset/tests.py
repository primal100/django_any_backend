from ..base import PickleDBTest
from testapp.models import Track
from sql_testapp.models import Track as SQLTrack

class PickleDBQuerysetTests(PickleDBTest):

    def test_count(self):
        qs1 = SQLTrack.objects
        qs2 = Track.objects
        self.assertCountEqual(qs1, qs2)

    def test_complex_count(self):
        filters = {"artist": 1}
        excludes = {"album": "Achtung Baby"}
        qs1 = SQLTrack.objects.filter(**filters).exclude(**excludes)
        qs2 = Track.objects.filter(**filters).exclude(**excludes)
        self.assertCountEqual(qs1, qs2, **self.override_settings)

    def test_all(self):
        qs1 = SQLTrack.objects.all()
        qs2 = Track.objects.all()
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_order(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_reverse_order(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.all().order_by(*order_by).reverse()
        qs2 = Track.objects.all().order_by(*order_by).reverse()
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_filter(self):
        filters = {"artist": 1}
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.filter(**filters).order_by(*order_by)
        qs2 = Track.objects.filter(**filters).order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_exclude(self):
        order_by = ["release_date", 'name']
        excludes = {"album": "Achtung Baby"}
        qs1 = SQLTrack.objects.exclude(**excludes).order_by(*order_by)
        qs2 = Track.objects.exclude(**excludes).order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_paginate_multi(self):
        order_by = ["release_date", 'name']
        pagination = (4, 8)
        qs1 = SQLTrack.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
        qs2 = Track.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_complex_qs(self):
        filters = {"artist": 1}
        excludes = {"album": "Achtung Baby"}
        order_by = ["release_date", 'name']
        pagination = (0, 8)
        qs1 = SQLTrack.objects.filter(**filters).exclude(**excludes).order_by(
            *order_by).reverse()[pagination[0]:pagination[1]]
        qs2 = Track.objects.filter(**filters).exclude(**excludes).order_by(
            *order_by).reverse()[pagination[0]:pagination[1]]
        self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_paginate_one(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        index = 2
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertOneEqual(qs1, qs2, index, fields, **self.override_settings)

    def test_get_result(self):
        filters = {"name": "Blackened"}
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertGetEqual(qs1, qs2, fields, **self.override_settings)

    def test_first(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertFirstEqual(qs1, qs2, fields, **self.override_settings)

    def test_last(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertLastEqual(qs1, qs2, fields, **self.override_settings)

    def test_exists(self):
        filters = {"name": "Blakened"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertExistsEqual(qs1, qs2, **self.override_settings)
        filters = {"name": "Blackened"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertExistsEqual(qs1, qs2, **self.override_settings)

    def test_values(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertValuesEqual(qs1, qs2)

    def test_value_lists(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertValueListEqual(qs1, qs2)

    """def test_none(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertNoneEqual(qs1, qs2, **self.override_settings)"""

    """def test_select_related(self):
        pass"""

    """def test_prefetch_related(self):
        pass"""

    """def test_update(self):
        filters = {"composer": "U2", "albumid": 232}
        params = {"unitprice": 1.10}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertQsUpdateEqual(qs1, qs2, params, **self.override_settings)"""

    """def test_create_delete(self):
        params = {"name": "Koyaanisqatsi", "albumid": 347, "mediatypeid": 2, "genreid": 10,
                        "composer": "Philip Glass", "milliseconds": 206005, "bytes": 3305164, "unitprice": "0.99"}
        qs1 = SQLTrack.objects.filter(**params)
        qs2 = Track.objects.filter(**params)
        self.assertQsDeleteEqual(qs1, qs2, **self.override_settings)
        self.assertQsCreateEqual(SQLTrack, Track, params, **self.override_settings)"""

    """def test_bulk_create_delete(self):

        objs1 = SQLTrack(name = "Go Down", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
            milliseconds = 331180, bytes = 10847611, unitprice = 0.99),
        SQLTrack(name = "Dog Eat Dog", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
            milliseconds = 215196, bytes = 7032162, unitprice = 0.99),
        SQLTrack(name = "Let There Be Rock", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
               milliseconds = 366654, bytes = 12021261, unitprice = 0.99),
        SQLTrack(name = "Bad Boy Boogie", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 267728, bytes = 8776140, unitprice = 0.99),
        SQLTrack(name = "Overdose", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 369319, bytes =12066294, unitprice = 0.99),
        SQLTrack(name = "Problem Child", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 325041, bytes = 10617116, unitprice = 0.99),
        SQLTrack(name = "Hell Ain't A Bad Place To Be", albumid = 4, mediatypeid = 1, genreid = 1,
               composer = "AC/DC", milliseconds = 254380, bytes = 8331286, unitprice = 0.99),

        objs2 = Track(name = "Go Down", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
            milliseconds = 331180, bytes = 10847611, unitprice = 0.99),
        Track(name = "Dog Eat Dog", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
            milliseconds = 215196, bytes = 7032162, unitprice = 0.99),
        Track(name = "Let There Be Rock", albumid = 4, mediatypeid = 1, genreid = 1, composer = "AC/DC",
               milliseconds = 366654, bytes = 12021261, unitprice = 0.99),
        Track(name = "Bad Boy Boogie", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 267728, bytes = 8776140, unitprice = 0.99),
        Track(name = "Overdose", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 369319, bytes =12066294, unitprice = 0.99),
        Track(name = "Problem Child", albumid = 4, mediatypeid = 1, genreid = 1, composer = 'AC/DC',
                milliseconds = 325041, bytes = 10617116, unitprice = 0.99),
        Track(name = "Hell Ain't A Bad Place To Be", albumid = 4, mediatypeid = 1, genreid = 1,
               composer = "AC/DC", milliseconds = 254380, bytes = 8331286, unitprice = 0.99),

        filters = {"composer": "AC/DC"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertQsDeleteEqual(qs1, qs2, **self.override_settings)
        self.assertBulkCreateEqual(SQLTrack, Track, objs1, objs2)"""

    """def test_get_or_create(self):
        params = {"name": "Highway To Hell", "albumid": 4, "mediatypeid": 1, "genreid": 1, "composer": "AC/DC",
                  "milliseconds": 331180, "bytes": 10847611, "unitprice": "0.99"}
        self.assertGetOrCreateEqual(SQLTrack, Track, params, **self.override_settings)
        self.assertGetOrCreateEqual(SQLTrack, Track, params, **self.override_settings)

    def test_update_or_create(self):
        params = {"name": "Thunderstruck", "albumid": 4, "mediatypeid": 1, "genreid": 1, "composer": "AC/DC",
                  "milliseconds": 331180, "bytes": 10847611, "unitprice": "0.99"}
        defaults1 = {"albumid": 5}
        defaults2 = {"albumid": 6}
        self.assertUpdateOrCreateEqual(SQLTrack, Track, defaults1, params, **self.override_settings)
        self.assertUpdateOrCreateEqual(SQLTrack, Track, defaults2, params, **self.override_settings)

    def test_annotate_aggregrate(self):
        pass"""