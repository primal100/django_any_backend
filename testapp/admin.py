from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from any_backend.admin import ModelAdmin as CustomMA
from models import Country, Person, Footballer, Company

class FootballerAdmin(TabularInline):
    list_display = ('name', 'club', 'age')
    model = Footballer
    can_delete = True
    fields = ('name', 'club', 'age')

class CountryAdmin(CustomMA):
    list_display = ('name', 'continent', 'city')
    inlines = (FootballerAdmin, )
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

admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)