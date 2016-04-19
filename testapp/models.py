from __future__ import unicode_literals

from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    type = models.IntegerField(choices=((0, 'Solo'), (1, 'Group')))
    genre = models.CharField(max_length=15)

    any_backend = 'pickle_db'
    max_per_request = 100

    def __str__(self):
        return self.name

class Track(models.Model):
    artist = models.ForeignKey(Artist, related_name='tracks')
    album = models.CharField(max_length=25)
    name = models.CharField( max_length=200)
    release_date = models.DateField(blank=True, null=True)

    any_backend = 'pickle_db'
    max_per_request = 100

    def __str__(self):
        return self.name


class Playlist(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    rating = models.IntegerField()
    added = models.DateTimeField(auto_now_add=True)
    tracks = models.ManyToManyField(Track, related_name='playlists')

    any_backend = 'pickle_db'
    max_per_request = 100

    def __str__(self):
        return self.name

