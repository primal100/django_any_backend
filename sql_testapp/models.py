from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=50)
    alpha2 = models.CharField(max_length=2, primary_key=True)
    numeric = models.IntegerField()

    def __str__(self):
        return self.name

class Subdivision(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    country = models.ForeignKey(Country)

    def __str__(self):
        return self.name