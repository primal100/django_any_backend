from __future__ import unicode_literals

from django.db import models

class Album(models.Model):
    albumid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=160)
    artistid = models.ForeignKey('Artist')

class Artist(models.Model):
    artistid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

class Customer(models.Model):
    customerid = models.IntegerField(primary_key=True)
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=20)
    company = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=70, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    postalcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    email = models.CharField(max_length=60)
    supportrepid = models.ForeignKey('Employee', blank=True, null=True)

class Employee(models.Model):
    employeeid = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=20)
    firstname = models.CharField(max_length=20)
    title = models.CharField(max_length=30, blank=True, null=True)
    reportsto = models.ForeignKey('self',blank=True, null=True)
    birthdate = models.DateTimeField(blank=True, null=True)
    hiredate = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=70, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    postalcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)

class Genre(models.Model):
    genreid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

class Invoice(models.Model):
    invoiceid = models.IntegerField(primary_key=True)
    customerid = models.ForeignKey(Customer)
    invoicedate = models.DateTimeField()
    billingaddress = models.CharField(max_length=70, blank=True, null=True)
    billingcity = models.CharField(max_length=40, blank=True, null=True)
    billingstate = models.CharField(max_length=40, blank=True, null=True)
    billingcountry = models.CharField(max_length=40, blank=True, null=True)
    billingpostalcode = models.CharField( max_length=10, blank=True, null=True)
    total = models.DecimalField(max_digits=2, decimal_places=2)

class Invoiceline(models.Model):
    invoicelineid = models.IntegerField(primary_key=True)
    invoiceid = models.ForeignKey(Invoice)
    trackid = models.ForeignKey('Track')
    unitprice = models.DecimalField(max_digits=2, decimal_places=2)
    quantity = models.IntegerField()

class Mediatype(models.Model):
    mediatypeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

class Playlist(models.Model):
    playlistid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

class Playlisttrack(models.Model):
    playlistid = models.ForeignKey(Playlist)
    trackid = models.ForeignKey('Track')

    class Meta:
        unique_together = (('playlistid', 'trackid'),)

class Track(models.Model):
    trackid = models.IntegerField(primary_key=True)
    playlist = models.ManyToManyField(Playlist, through=Playlisttrack, related_name='tracks')
    name = models.CharField( max_length=200)
    albumid = models.ForeignKey(Album, blank=True, null=True)
    mediatypeid = models.ForeignKey(Mediatype)
    genreid = models.ForeignKey(Genre, blank=True, null=True)
    composer = models.CharField(max_length=220, blank=True, null=True)
    milliseconds = models.IntegerField()
    bytes = models.IntegerField(blank=True, null=True)
    unitprice = models.DecimalField(max_digits=2, decimal_places=2)