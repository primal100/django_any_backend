import pickle
import os
from operator import itemgetter
from any_backend.client import Client
from django.core.cache import caches

class PickleDB(Client):

    def create_db(self, db_name):
        self.cache = caches['pickle_cache']
        self.filename = db_name
        self._update_data(new=True)

    def delete_db(self, db_name):
        os.remove(db_name)

    def db_exists(self, db_name):
        self.filename = db_name
        return os.path.exists(self.filename)

    def setup(self, db_name):
        self.filename = db_name
        self.cache = caches['pickle_cache']

    def _get_data(self, model=None):
        if model:
            data = self.cache.get(model._meta.model_name, default=None)
            if not data:
                data = self.cache.get('all', default=None)
                if data:
                    data = data[model._meta.db_table]
                    self.cache.set(model._meta.model_name, data, 15)
        else:
            data = self.cache.get('all', default=None)
        if not data:
            with open(self.filename, 'rb') as handle:
                data = pickle.load(handle)
                self.cache.set('all', data, 15)
            if model:
                data = data[model._meta.db_table]
                self.cache.set(model._meta.model_name, data, 15)
        return data

    def _update_data(self, model=None, new_data=None, new=False):
        if not new:
            self.data = getattr(self, 'data', self._get_data())
        if model and new_data != None:
            self.data[model._meta.db_table] = new_data
        elif new:
            self.data = {}
            for model in self.models:
                self.data[model._meta.db_table] = []
        else:
            raise TypeError('Update pickle file failed. Model and new arguments cannot both be None')
        with open(self.filename, 'wb') as handle:
            pickle.dump(self.data, handle)
        self.cache.clear()

    def create_bulk(self, model, objects):
        model_list = self._get_data(model=model)
        if model._meta.pk.auto_created:
            pk_fieldname =  model._meta.pk.attname
            if model_list:
                last_pk = sorted(model_list, key=itemgetter(pk_fieldname), reverse=True)[0][pk_fieldname]
            else:
                last_pk = -1
            for i, object in enumerate(objects):
                last_pk += 1
                object[pk_fieldname] = last_pk
                objects[i] = object
        model_list += objects
        self._update_data(model=model, new_data=model_list)
        return objects

    def get_pks(self, model, filters):
        objects = self._get_data(model=model)
        objects = filters.apply(objects)
        return objects

    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        if model._meta.model_name.lower() == 'subdivision':
            pass
        objects = self._get_data(model=model)
        objects, count = self.apply_all(objects, filters=filters, distinct=distinct, order_by=order_by, paginator=paginator)
        for fk_fieldname, fk_columnname, fk_model, fk_pkfield in self.get_related(model):
            for i, object in enumerate(objects):
                fk_value = object[fk_columnname]
                kwargs = {fk_pkfield: fk_value}
                object[fk_fieldname] = fk_model.objects.filter(**kwargs).get()
                objects[i] = object
        return objects, count

    def delete_bulk(self, model, filters):
        data = self._get_data(model=model)
        objects = filters.apply(data)
        for object in objects:
            data.remove(object)
        self._update_data(model=model, new_data=data)
        return objects

    def update_bulk(self, model, filters, update_with=()):
        data = self._get_data(model=model)
        objects = filters.apply(data)
        for i, object in enumerate(data):
            if object in objects:
                data[i] = update_with.apply(object)
        self._update_data(model=model, new_data=data)
        return objects