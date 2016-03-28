# Django Any Backend #

DJANGO_ANY_BACKEND is designed to allow the use of models with non-database backends in Django. The first objective is to allow the use of all the Django Queryset API (https://docs.djangoproject.com/en/1.9/ref/models/querysets/) with these models so that they work with: 

* Django ModelForm
* Django built-in crud views (CreateView, UpdateView, DeleteView, ListView and DetailView)
* Django ModelAdmin
* Django ModelSerializers (thus Django Rest Framework)

The second objective is to make it as simple as possible to implement a new custom backend by subclassing one class and providing the required crud functions. This was influenced by how custom backends can be implented in Flask.

# Getting Started #

"""python

from django_any_backend import 

