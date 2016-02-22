from django.contrib import admin
from django.contrib.admin import ModelAdmin
from any_backend.admin import ModelAdmin as CustomMA
from models import Country, Person, Footballer

class CountryAdmin(CustomMA):
    list_display = ('name', 'continent', 'city')

class FootballerAdmin(CustomMA):
    list_display = ('name', 'country', 'club', 'age')

class PersonAdmin(ModelAdmin):
    list_display = ('name', 'age', 'job')

admin.site.register(Footballer, FootballerAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Country, CountryAdmin)