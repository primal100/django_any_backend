from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from any_backend.admin import ModelAdmin as CustomMA
from models import Country, Person, Subdivision, Company

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

class PersonAdmin(TabularInline):
    list_display = ('name', 'company', 'age', 'job')
    model = Person
    can_delete = True
    fields = ('name', 'company', 'age', 'job')

class CompanyAdmin(ModelAdmin):
    list_display = ('name', 'location')
    inlines = (PersonAdmin, )
    list_per_page = 3

admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)