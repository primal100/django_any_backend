class Connection(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def setup(self):
        pass


    def create(self, object=None, model=None, db_config=None):
        """

        :param params:
        :param kwargs:
        :return: object The object which was successfully created
        """

        raise NotImplementedError('You must implement a create function in your connection class')

    def list(self, filters, model=None, db_config=None, app=None, app_model=None, out_cols=None, group_by=None,
             order_by=None, limit=None, offset=None, page_num=None):
        raise NotImplementedError('You have not implemented a list function in your connection class')

    def delete(self, id, model=None, db_config=None, app=None, app_model=None):
        raise NotImplementedError('You have not implemented a delete function in your connection class')

    def update(self, id, update_with=None, model=None, db_config=None, app=None, app_model=None):
        raise NotImplementedError('You have not implemented an update function in your connection class')

    def create_bulk(self, filters, objects=None, model=None, db_config=None, app=None, app_model=None):
        created_objects = []
        for obj in objects:
            obj = self.create(object=obj, model=None, db_config=db_config)
            created_objects.append(obj)
        return object

    def get_pks(self, filters, model, db_config):
        raise NotImplementedError("You have not implemented a get_pks function")

    def delete_bulk(self, filters, model=None, db_config=None, app=None, app_model=None):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully deleted
        """
        ids = self.get_pks(filters, model, db_config)

        deleted_objects = []

        for id in ids:
            obj = self.delete(id, model=model, db_config=db_config)
            deleted_objects.append(obj)
        return deleted_objects

    def update_bulk(self, filters, model=None, update_with=None, db_config=None, app=None, app_model=None, ):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully updated
        """
        ids = self.get_pks(filters, model, db_config)

        for id in ids:
            self.update(id, model=model, update_with=update_with, db_config=db_config)
        return ids

    def enter(self):
        pass

    def exit(self, exc_type=None, exc_val=None, exc_tb=None):
        pass