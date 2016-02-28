from django.contrib import admin
from django.contrib.admin import TabularInline
from any_backend.admin import ModelAdmin as CustomMA
"""from models import Country, Subdivision

class SubdivisionAdmin(TabularInline):
    list_display = ('name', 'club', 'age')
    model = Subdivision
    can_delete = True
    fields = ('name', 'code', 'country', 'type')

class CountryAdmin(CustomMA):
    list_display = ('name', 'alpha2', 'numeric')
    inlines = (SubdivisionAdmin, )
    list_max_show_all = True
    list_per_page = 3

admin.site.register(Country, CountryAdmin)"""