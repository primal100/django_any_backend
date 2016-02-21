class Client(object):
    def __init__(self, cursor, db_config):
        self.cursor = cursor
        self.db_config = db_config

    def create_test(self, db_name):
        """
        Run when manage.py tests is run
        """
        pass

    def setup(self, db_config):
        """
        Run when Django app is started
        """
        pass

    def create(self, model, object, app_model):
        """

        :param params:
        :param kwargs:
        :return: object The object which was successfully created
        """

        raise NotImplementedError('You must implement a create function in your connection class')


    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        raise NotImplementedError('You have not implemented a list function in your connection class')

    def delete(self, model, id):
        raise NotImplementedError('You have not implemented a delete function in your connection class')

    def update(self, model, id, update_with):
        raise NotImplementedError('You have not implemented an update function in your connection class')

    def apply_all(self, objects, filters=None, distinct=None, order_by=None, paginator=None):
        if filters:
            objects = filters.apply(objects)
        if distinct:
            objects = distinct.apply(objects)
        count = len(objects)
        if order_by:
            objects = order_by.apply(objects)
        if paginator:
            objects = paginator.apply(objects)
        return objects, count

    def get_pks(self, model, filters):
        raise NotImplementedError("You have not implemented a get_pks function")

    def create_bulk(self, model, objects):
        created_objects = []
        for obj in objects:
            obj = self.create(model, object)
            created_objects.append(obj)
        return object

    def delete_bulk(self, model, filters):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully deleted
        """
        ids = self.get_pks(model, filters)

        deleted_objects = []

        for id in ids:
            obj = self.delete(id, model)
            deleted_objects.append(obj)
        return deleted_objects

    def update_bulk(self, model, filters, update_with=()):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully updated
        """
        ids = self.get_pks(model, filters)

        for id in ids:
            self.update(model, id, update_with=update_with)
        return ids

    def enter(self):
        pass

    def close(self, exc_type=None, exc_val=None, exc_tb=None):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass