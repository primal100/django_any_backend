from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=50)
    alpha2 = models.CharField(max_length=2, primary_key=True)
    numeric = models.IntegerField()

    non_db = 'pickle_db'
    max_per_request = None

    def __str__(self):
        return self.name

class Subdivision(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    country = models.ForeignKey(Country)

    non_db = 'pickle_db'
    max_per_request = 100

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=25)
    location = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class Person(models.Model):
    company = models.ForeignKey(Company)
    name = models.CharField(max_length=25)
    age = models.IntegerField()
    job = models.CharField(max_length=25)

    def __str__(self):
        return self.name