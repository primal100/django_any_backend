from utils import getvalue

class Client(object):
    default_compiler = 'django_any_backend.backends.compiler'

    def __init__(self, db_config):
        self.db_config = db_config
        self.name = self.db_config['NAME']
        self.compiler_module = self.db_config.get('COMPILER', None) or self.default_compiler

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
        :return: count The number of objects successfully deleted
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
        :return: count The number of objects successfully updated
        """
        ids = self.get_pks(model, filters)

        for id in ids:
            self.update(model, id, update_with=update_with)
        return len(ids)

    def apply_all(self, objects, filters=None, distinct=None, order_by=None, paginator=None, count_only=False):
        if filters:
            objects = filters.apply(objects)
        if distinct:
            objects = distinct.apply(objects)
        count = len(objects)
        if count_only:
            return count
        if order_by:
            objects = order_by.apply(objects)
        if paginator:
            objects = paginator.apply(objects)
        return objects, count

    def get_related_one(self, model):
        forward_fields = model._meta._forward_fields_map
        column_names = []
        for fieldname, field in forward_fields.iteritems():
            if field.is_relation and not field.many_to_many:
                column_name = field.attname
                if column_name not in column_names:
                    column_names.append(column_name)
                    fk_model = field.related_model
                    fk_pk = fk_model._meta.pk
                    yield fieldname, column_name, fk_model, fk_pk


    def convert_to_tuple(self, object, fields):
        values = []
        for field in fields:
            value = object
            for attr in field:
                value = getvalue(value, attr)
            values.append(value)
        return tuple(values)

    def convert_to_tuples(self, objects, field_names):
        if objects:
            if type(objects[0]) == tuple:
                return objects
            elif type(objects[0]) == list:
                for index, obj in enumerate(objects):
                    objects[index] = tuple(obj)
                return objects
            else:
                list_of_tuples = []
                for object in objects:
                    list_of_tuples.append(self.convert_to_tuple(object, field_names))
                return list_of_tuples
        else:
            return []

    def close(self):
        """
        Run each time a connection to the backend is closed.
        """
        pass

    def flush(self, table, sequences, allow_cascade):
        """
        Remove all instances in a table, this is only required for certain management commands such flushsql or if keepdb is used with the test command. Most likely not required if backend is a remote api.
        """
        raise NotImplementedError("You have not implemented a flush function in your client class")

    def commit(self):
        pass

    def rollback(self):
        pass