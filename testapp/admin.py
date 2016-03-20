from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from models import Artist, Playlist, Track

class PlaylistAdmin(ModelAdmin):
    list_display = ('name', 'rating')
    filter_horizontal = ('tracks',)

class TrackAdmin(ModelAdmin):
    list_max_show_all = True

class InlineTrackAdmin(TabularInline):
    list_display = ('name', 'album', 'release_date')
    model = Track
    can_delete = True
    fields = ('name', 'album', 'release_date')

class ArtistAdmin(ModelAdmin):
    list_display = ('name', 'type', 'genre')
    inlines = (InlineTrackAdmin, )

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Track, TrackAdmin)