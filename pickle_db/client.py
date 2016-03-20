import pickle
from any_backend.filters import Filters, Filter
from operator import itemgetter
from any_backend.client import Client
from django.core.cache import caches

class PickleDB(Client):

    def setup(self, db_name):
        self.filename = db_name
        self.cache = caches['pickle_cache']

    def get_data(self, model=None):
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

    def update_data(self, new_data, model=None):
        if model:
            self.data = getattr(self, 'data', self.get_data())
            self.data[model._meta.db_table] = new_data
        else:
            self.data = new_data
        with open(self.filename, 'wb') as handle:
            pickle.dump(self.data, handle)
        self.cache.clear()

    def create_bulk(self, model, objects):
        model_list = self.get_data(model=model)
        pk_fieldname =  model._meta.pk.attname
        if model._meta.pk.auto_created:
            if model_list:
                last_pk = sorted(model_list, key=itemgetter(pk_fieldname), reverse=True)[0][pk_fieldname]
            else:
                last_pk = -1
            for i, object in enumerate(objects):
                last_pk += 1
                pk = object.get(pk_fieldname, None)
                if not pk:
                    object[pk_fieldname] = last_pk
                    objects[i] = object
                elif pk > last_pk:
                    last_pk = pk + 1
        model_list += objects
        self.update_data(model=model, new_data=model_list)
        pks = [x[pk_fieldname] for x in objects]
        return pks

    def get_pks(self, model, filters):
        objects = self.get_data(model=model)
        objects = filters.apply(objects)
        return objects

    def count(self, model, filters, distinct=None):
        objects = self.get_data(model=model)
        count = self.apply_all(objects, filters=filters, distinct=distinct, count_only=True)
        return count

    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        objects = self.get_data(model=model)
        objects, count = self.apply_all(objects, filters=filters, distinct=distinct, order_by=order_by, paginator=paginator)
        for fk_fieldname, fk_columnname, fk_model, fk_pkfield in self.get_related_one(model):
            fk_values = []
            for obj in objects:
                fk_value = obj[fk_columnname]
                fk_values.append(fk_value)
            filters = Filters()
            filters.append(Filter(fk_pkfield, 'in', False, fk_values))
            related_objects = self.list(fk_model, filters)[0]
            for i, obj in enumerate(objects):
                obj[fk_fieldname] = [x for x in related_objects if x[fk_pkfield.attname] == obj[fk_columnname]][0]
                objects[i] = obj
        return objects, count

    def delete_bulk(self, model, filters):
        data = self.get_data(model=model)
        objects = filters.apply(data)
        for object in objects:
            data.remove(object)
        self.update_data(model=model, new_data=data)
        return len(objects)

    def update_bulk(self, model, filters, update_with=()):
        data = self.get_data(model=model)
        objects = filters.apply(data)
        for i, object in enumerate(data):
            if object in objects:
                data[i] = update_with.apply(object)
        self.update_data(model=model, new_data=data)
        return len(objects)

    def flush(self, table, sequences, allow_cascade):
        data = self.get_data()
        data[table] = []
        self.update_data(data)
