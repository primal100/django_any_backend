class Client(object):
    def __init__(self, cursor, db_config):
        self.cursor = cursor
        self.db_config = db_config

    def setup(self):
        pass

    def create(self, object=None, model=None, app_model=None):
        """

        :param params:
        :param kwargs:
        :return: object The object which was successfully created
        """

        raise NotImplementedError('You must implement a create function in your connection class')


    def list(self, filters, model=None, model_name=None, paginator=None, orderby=None, distinct=None,
             app_model=None, out_cols=None):
        raise NotImplementedError('You have not implemented a list function in your connection class')

    def delete(self, id, model=None, app_model=None):
        raise NotImplementedError('You have not implemented a delete function in your connection class')

    def update(self, id, update_with=None, model=None, app_model=None):
        raise NotImplementedError('You have not implemented an update function in your connection class')

    def apply_all(self, objects, filters=None, distinct=None, orderby=None, paginator=None):
        if filters:
            objects = filters.apply(objects)
        if distinct:
            objects = distinct.apply(objects)
        if orderby:
            objects = orderby.apply(objects)
        if paginator:
            objects = paginator.apply(objects)
        return objects

    def create_bulk(self, filters, objects=None, model=None, app_model=None):
        created_objects = []
        for obj in objects:
            obj = self.create(object=obj, model=None, app_model=app_model)
            created_objects.append(obj)
        return object

    def get_pks(self, filters, model, app_model=None):
        raise NotImplementedError("You have not implemented a get_pks function")

    def delete_bulk(self, filters, model=None, app_model=None):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully deleted
        """
        ids = self.get_pks(filters, model, app_model=app_model)

        deleted_objects = []

        for id in ids:
            obj = self.delete(id, model=model)
            deleted_objects.append(obj)
        return deleted_objects

    def update_bulk(self, filters, model=None, update_with=None, app_model=None):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully updated
        """
        ids = self.get_pks(filters, model, app_model=app_model)

        for id in ids:
            self.update(id, model=model, update_with=update_with, app_model=app_model)
        return ids

    def enter(self):
        pass

    def exit(self, exc_type=None, exc_val=None, exc_tb=None):
        pass