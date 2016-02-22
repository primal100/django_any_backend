from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=25)
    continent = models.CharField(max_length=13)
    city = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class Footballer(models.Model):
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=30)
    club = models.CharField(max_length=25)
    age = models.IntegerField()

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=25)
    age = models.IntegerField()
    job = models.CharField(max_length=25)

    def __str__(self):
        return self.name