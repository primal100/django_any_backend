from ..base import PickleDBTest
from testapp.models import Track, Artist, Playlist
from sql_testapp.models import Track as SQLTrack, Artist as SQLArtist, Playlist as SQLPlaylist

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
        self.assertCountEqual(qs1, qs2)

    def test_all(self):
        qs1 = SQLTrack.objects.all()
        qs2 = Track.objects.all()
        self.assertQuerysetsEqual(qs1, qs2)

    def test_order(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2)

    def test_reverse_order(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.all().order_by(*order_by).reverse()
        qs2 = Track.objects.all().order_by(*order_by).reverse()
        self.assertQuerysetsEqual(qs1, qs2)

    def test_filter(self):
        filters = {"artist": 1}
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.filter(**filters).order_by(*order_by)
        qs2 = Track.objects.filter(**filters).order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2)

    def test_exclude(self):
        order_by = ["release_date", 'name']
        excludes = {"album": "Achtung Baby"}
        qs1 = SQLTrack.objects.exclude(**excludes).order_by(*order_by)
        qs2 = Track.objects.exclude(**excludes).order_by(*order_by)
        self.assertQuerysetsEqual(qs1, qs2)

    def test_paginate_multi(self):
        order_by = ["release_date", 'name']
        pagination = (4, 8)
        qs1 = SQLTrack.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
        qs2 = Track.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
        self.assertQuerysetsEqual(qs1, qs2)

    def test_complex_qs(self):
        filters = {"artist": 1}
        excludes = {"album": "Achtung Baby"}
        order_by = ["release_date", 'name']
        pagination = (0, 8)
        qs1 = SQLTrack.objects.filter(**filters).exclude(**excludes).order_by(
            *order_by).reverse()[pagination[0]:pagination[1]]
        qs2 = Track.objects.filter(**filters).exclude(**excludes).order_by(
            *order_by).reverse()[pagination[0]:pagination[1]]
        self.assertQuerysetsEqual(qs1, qs2)

    def test_paginate_one(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        index = 2
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertOneEqual(qs1, qs2, index, fields)

    def test_get_result(self):
        filters = {"name": "Blackened"}
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertGetEqual(qs1, qs2, fields)

    def test_first(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertFirstEqual(qs1, qs2, fields)

    def test_last(self):
        order_by = ["release_date", 'name']
        fields = ['name', 'artist_id', 'album', 'release_date']
        qs1 = SQLTrack.objects.order_by(*order_by)
        qs2 = Track.objects.order_by(*order_by)
        self.assertLastEqual(qs1, qs2, fields)

    def test_exists(self):
        filters = {"name": "Blakened"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertExistsEqual(qs1, qs2)
        filters = {"name": "Blackened"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertExistsEqual(qs1, qs2)

    def test_values(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by).values()
        qs2 = Track.objects.order_by(*order_by).values()
        self.assertQuerysetsEqual(qs1, qs2)

    def test_value_lists(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by).values_list()
        qs2 = Track.objects.order_by(*order_by).values_list()
        self.assertQuerysetsEqual(qs1, qs2)

    def test_none(self):
        order_by = ["release_date", 'name']
        qs1 = SQLTrack.objects.order_by(*order_by).none()
        qs2 = Track.objects.order_by(*order_by).none()
        self.assertQuerysetsEqual(qs1, qs2)

    def test_select_related(self):
        filters = {"name": "Blackened"}
        fields = ['name', 'artist_id', 'album', 'release_date',
                  {'related': 'artist', 'fields': ['id', 'name', 'genre', 'type']}]
        related = 'artist'
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertGetEqual(qs1, qs2, fields)
        qs1 = qs1.select_related(related)
        qs2 = qs1.select_related(related)
        self.assertGetEqual(qs1, qs2, fields)

    def test_update(self):
        filters = {"album": "The Black Album"}
        params = {"album": "Metallica"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        after_qs1 = SQLTrack.objects.filter(**params)
        after_qs2 = Track.objects.filter(**params)
        self.assertQsUpdateEqual(qs1, qs2, after_qs1, after_qs2, params)

    def test_create_delete(self):
        params1 = {"album": "Live And Dangerous", "name": "The Boys Are Back In Town", "release_date": "1978-06-02"}
        fieldnames = ['album', 'name', 'release_date']
        params2 = params1.copy()
        artist_params = {"id": 10}
        artist1 = SQLArtist.objects.filter(**artist_params).get()
        artist2 = Artist.objects.filter(**artist_params).get()
        qs1 = SQLTrack.objects.filter(**params1)
        qs2 = Track.objects.filter(**params2)
        params1['artist'] = artist1
        params2['artist'] = artist2
        self.assertQsDeleteEqual(qs1, qs2)
        self.assertQsCreateEqual(SQLTrack, Track, params1, params2, fieldnames)

    def test_bulk_create_delete(self):
        artist_params = {"id": 5}
        artist1 = SQLArtist.objects.filter(**artist_params).get()
        artist2 = Artist.objects.filter(**artist_params).get()
        objects1 = [
        SQLTrack(name = "Black Dog", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "Rock N Roll", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "The Battle Of Evermore", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "Stairway To Heaven", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "Misty Mountain Hop", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "Four Sticks", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "Going To Caliornia", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
        SQLTrack(name = "When The Levee Breaks", artist = artist1, album="Led Zeppelin 4", release_date = "1971-11-08"),
               ]
        objects2 = [
        Track(name = "Black Dog", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "Rock N Roll", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "The Battle Of Evermore", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "Stairway To Heaven", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "Misty Mountain Hop", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "Four Sticks", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "Going To Caliornia", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
        Track(name = "When The Levee Breaks", artist = artist2, album="Led Zeppelin 4", release_date = "1971-11-08"),
               ]
        filters = {"album": "Led Zeppelin 4"}
        qs1 = SQLTrack.objects.filter(**filters)
        qs2 = Track.objects.filter(**filters)
        self.assertBulkCreateEqual(SQLTrack, Track, qs1, qs2, objects1, objects2)

    def test_get_or_create(self):
        params = {"name": "Rage Against The Machine", "type": 1, "genre": "Rock"}
        self.assertGetOrCreateEqual(SQLArtist, Artist, params)
        self.assertGetOrCreateEqual(SQLArtist, Artist, params)

    def test_update_or_create(self):
        params = {"name": "Metallica", "type": 1, "genre": "Heavy Metal"}
        defaults = {"genre": "Thrash Metal"}
        self.assertUpdateOrCreateEqual(SQLArtist, Artist, defaults, params)
        self.assertUpdateOrCreateEqual(SQLArtist, Artist, defaults, params)