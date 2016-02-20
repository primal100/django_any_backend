from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=25)
    continent = models.CharField(max_length=13)
    city = models.CharField(max_length=25)