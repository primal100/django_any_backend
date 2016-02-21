import pickle
from any_backend.client import Client

class PickleDB(Client):

    def initialize_new(self, db_name):
        self.filename = db_name
        self._update_data([])

    def setup(self, db_config):
        self.db_config = db_config
        self.filename = self.db_config['NAME']

    def _get_data(self):
        with open(self.filename, 'rb') as handle:
            data = pickle.load(handle)
        return data

    def _update_data(self, new_data):
        with open(self.filename, 'wb') as handle:
            pickle.dump(new_data, handle)

    def create_bulk(self, filters, objects=None, model=None, app_model=None):
        data = self._get_data()
        data.append(objects)
        self._update_data(data)
        return objects

    def list(self, filters, model=None, model_name=None, paginator=None, order_by=None, distinct=None,
             app_model=None, out_cols=None):
        objects = self._get_data()
        return self.apply_all(objects, filters=filters, distinct=distinct, order_by=order_by, paginator=paginator)

    def delete_bulk(self, filters, model=None, app_model=None):
        data = self._get_data()
        objects = filters.apply(data)
        for object in objects:
            data.remove(object)
        self.update(data)
        return objects

    def update_bulk(self, filters, model=None, update_with=None, app_model=None):
        data = self._get_data()
        objects = filters.apply(data)
        for i, object in enumerate(data):
            if object in objects:
                data[i] = update_with.apply(object)
        self.update(data)
        return objects