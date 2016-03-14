from any_backend.backends.schema import DatabaseSchemaEditor as BaseDatabaseSchemaEditor
import os

class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    def create_db(self, db_name):
        self.connection.client.setup(db_name)
        self.connection.client.update_data({})

    def delete_db(self, db_name):
        os.remove(db_name)

    def db_exists(self, db_name):
        self.connection.client.setup(db_name)
        return os.path.exists(db_name)

    def create_model(self, model):
        data = self.connection.client.get_data()
        table = model._meta.db_table
        if table in data.keys():
            raise NameError('Table %s already exists. Problem may be with introspection get_table_list function' % (table))
        else:
            data[table] = []
            self.connection.client.update_data(data)

    def delete_model(self, model):
        data = self.connection.client.get_data()
        table_name = model._meta.db_table
        if table_name in data.keys():
            del data[model._meta.db_table]
            self.connection.client.update_data(data)

    def alter_db_table(self, model, old_db_table, new_db_table):
        if old_db_table != new_db_table:
            data = self.connection.client.get_data()
            data[new_db_table] = data.pop(old_db_table)
            self.connection.client.update_data(data)
