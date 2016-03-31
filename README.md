# Django Any Backend #

DJANGO_ANY_BACKEND is designed to allow the use of models with non-database backends in Django. The first objective is to allow the use of all the Django Queryset API (https://docs.djangoproject.com/en/1.9/ref/models/querysets/) with these models so that they work with: 

* Django ModelForm
* Django built-in crud views (CreateView, UpdateView, DeleteView, ListView and DetailView)
* Django ModelAdmin
* Django ModelSerializers (thus Django Rest Framework)

The second objective is to make it as simple as possible to implement a new custom backend by subclassing one class and providing the required crud functions. This was influenced by how custom backends can be implented in Flask.

A sample app using Pickle as a backend is included for demonstration and test purposes.

# Getting Started #

Install the app with

```shell
pip install django-any-backend.
```

Import the django_any_backend Client object and override the key functions. There are two possible appraches for the write operations:

1.  Override create, update, delete (for individual objects) and get_pks. The default bulk functions will then loop through each object and run the required functions.
2.  Override create_bulk, delete_bulk and update_bulk. In this case the functions in option 1 are not required.

```python

from django_any_backend.client import Client

class CustomClient(Client):

    def setup(self, db_name):
        """
        Run every time connection to backend is made
        :param db_name: Name of backend (could be test db name, most likely ignored for external api)
        """
        self.name = db_name

    def create(self, model, object):
        """
        Creates a model instance. Not required if create_bulk is overridden.
        :param model: The model for which an instance is to be created
        :param object: A dictionary of arguments to create the object with
        :return: PK: Primary key of object which was created. Should raise exception if object cannot be created
        """
        raise NotImplementedError('You must implement a create func in your connection class')


    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        """
        Lists the instances of a model
        :param model: The model for which a list of instances is requested
        :param filters: A list of filter objects
        :param paginator: A BackendPaginator object with required pagination
        :param order_by: A list of orderby objects
        :param distinct: A list of columns for which distinct values are required
        :param out_cols: The list of output columns requested for each instance
        :return: List of instances in dict, object, list or tuples form
        :return: The number of instances after filtering and distinct, but before pagination
        """
        raise NotImplementedError('You have not implemented a list func in your client class')

    def delete(self, model, id):
        """
        Deletes the model by primary key. Not required if delete_bulk is overridden.
        :param model: The model for which an instance is to be deleted
        :param id: The primary key of the instance which is to be deleted
        :return: The id of the deleted object
        """
        raise NotImplementedError('You have not implemented a delete func in your client class')

    def update(self, model, id, update_with):
        """
        Updates a model instance. Not required if update_bulk is overridden.
        :param model: The model for which an instance is to be updated
        :param id: The pk of the instance to be updated
        :param update_with: A dictionary of keys and attributes to update
        :return: The pk of the updated object
        """
        raise NotImplementedError('You have not implemented an update func in your client class')

    def count(self, model, filters, distinct=None):
        """
        Counts the number of instances for a model
        :param model: The model who's instances are to be counted
        :param filters: A list of filter objects
        :param distinct: A list of columns which distinct values are to be counted
        :return: An integer of the number of objects after filtering and distinct
        """
        raise NotImplementedError('You have not implemented a count function in your client class')

    def get_pks(self, model, filters):
        """
        Returns a list of primary keys. Not required if both update_bulk and delete_bulk are overridden.
        :param model: The model for which primary keys are to be returned
        :param filters: A list of filters
        :return: A list of integers, the primary keys of the instances.
        """
        raise NotImplementedError("You have not implemented a get_pks function in your client class")

    def create_bulk(self, model, objects):
        """
        Bulk create a list of model instances. The default implementation loops through the objects and runs a custom create function. Only one of create or create_bulk needs to be implemented.
        :param model: The model for which objects are to be created
        :param objects: A list of dictionaries of model objects
        :return: A list of primary keys for the created objects.
        """
        pks = []
        pk_attname = model._meta.pk.attname
        for obj in objects:
            obj = self.create(model, obj)
            pks.append(getattr(obj, pk_attname))
        return pks

    def delete_bulk(self, model, filters):
        """
        Bulk delete a list of model instances. The default implementation runs the get_pks function, looping through the objects and runs a custom delete.
        :param kwargs:
        :return: ids The number of objects successfully deleted
        """
        ids = self.get_pks(model, filters)

        deleted_objects = []

        for id in ids:
            obj = self.delete(id, model)
            deleted_objects.append(obj)
        return len(deleted_objects)

    def update_bulk(self, model, filters, update_with=()):
        """
        Bulk delete a list of model instances. The default implementation runs the get_pks function, looping through the objects and runs a custom update function.
        :param params:
        :param kwargs:
        :return: ids The number of objects successfully updated
        """
        ids = self.get_pks(model, filters)

        for id in ids:
            self.update(model, id, update_with=update_with)
        return ids
```

In settings.py, add 'django_any_backend' to the list of installed apps,

Then add the custom client to the list of database backends:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'custom': {
        'ENGINE': 'django_any_backend.backends',
        'NAME': os.path.join(BASE_DIR, 'custom'),
        'CLIENT': 'mycustombackend.client.CustomClient',
        'MIGRATIONS': False,
    }
}
```

You need to add a database router in settings.py (https://docs.djangoproject.com/en/1.9/topics/db/multi-db/#using-routers). Django_Any_Backend comes with one built-in which you can use by adding the following line to settings.py.

```python
DATABASE_ROUTERS = ['django_any_backend.routers.BackendRouter']
```

If using this router, it is required to mark which models to route to the custom backend. This is done by adding non_db and max_per_request attributes to each model which will use a custom non-db backend. Use the name of the backend as specified above in the DATABASES attribute of settings.py.

In models.py:

```python
class Artist(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    type = models.IntegerField(choices=((0, 'Solo'), (1, 'Group')))
    genre = models.CharField(max_length=15)

    non_db = 'custom'
    max_per_request = 100

```

If max_per_request is set, big list requests will be broken up into chunks.

To enable migrations it is required to implement Introspection and Schema modules. Obviously not required if the backend is a remote api. Information about other features will be added soon, for now check out the example called testapp. 


# Contributions #

Django_any_backend still needs work. It has only been tested so far in Python 2.7 and Django 1.9.

More tests need to be written.

Although Django_any_backend has no restrictions on many_to_many, the pickle_db example doesn't support it so it can't be tested yet

Support for distinct fields needs to be tested.
