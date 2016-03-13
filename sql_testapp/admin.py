from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from models import Country, Subdivision

class SubdivisionAdmin(TabularInline):
    list_display = ('name', 'club', 'age')
    model = Subdivision
    can_delete = True
    fields = ('name', 'code', 'country', 'type')

class CountryAdmin(ModelAdmin):
    list_display = ('name', 'alpha2', 'numeric')
    inlines = (SubdivisionAdmin, )
    list_max_show_all = True
    list_per_page = 3

admin.site.register(Country, CountryAdmin)