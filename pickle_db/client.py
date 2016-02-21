import pickle
import os
from operator import itemgetter
from any_backend.client import Client

class PickleDB(Client):

    def create_test(self, db_name):
        self.filename = db_name
        self.models = self.db_config['MODELS']
        self._update_data(new=True)

    def setup(self, db_config):
        self.db_config = db_config
        self.filename = getattr(self, 'filename', self.db_config['NAME'])
        self.models = self.db_config['MODELS']
        if not os.path.exists(self.filename):
            self._update_data(new=True)

    def _get_data(self, model=None):
        with open(self.filename, 'rb') as handle:
            self.data = pickle.load(handle)
        if model:
            return self.data[model._meta.model_name]
        return self.data

    def _update_data(self, model=None, new_data=None, new=False):
        if not new:
            self.data = getattr(self, 'data', self._get_data())
        if model and new_data:
            self.data[model._meta.model_name] = new_data
        elif new:
            self.data = {}
            for model in self.models:
                self.data[model.lower()] = []
        else:
            raise TypeError('Update pickle file failed. Model and new arguments cannot both be None')
        with open(self.filename, 'wb') as handle:
            pickle.dump(self.data, handle)

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

    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        objects = self._get_data(model=model)
        return self.apply_all(objects, filters=filters, distinct=distinct, order_by=order_by, paginator=paginator)

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