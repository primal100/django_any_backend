from django.db.backends.base.schema import BaseDatabaseSchemaEditor

class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    def create_db(self, db_name):
        pass

    def delete_db(self, db_name):
        pass

    def db_exists(self, db_name):
        pass

    def create_model(self, model):
        pass

    def delete_model(self, model):
        pass

    def alter_unique_together(self, model, old_unique_together, new_unique_together):
        pass

    def alter_index_together(self, model, old_index_together, new_index_together):
        pass

    def _delete_composed_index(self, model, fields, constraint_kwargs, sql):
        pass

    def alter_db_table(self, model, old_db_table, new_db_table):
        pass

    def alter_db_tablespace(self, model, old_db_tablespace, new_db_tablespace):
        pass

    def add_field(self, model, field):
        if field.many_to_many and field.remote_field.through._meta.auto_created:
            self.create_model(field.remote_field.through)

    def remove_field(self, model, field):
        if field.many_to_many and field.remote_field.through._meta.auto_created:
                self.delete_model(field.remote_field.through)

    def alter_field(self, model, old_field, new_field, strict=False):
        old_db_params = old_field.db_parameters(connection=self.connection)
        old_type = old_db_params['type']
        new_db_params = new_field.db_parameters(connection=self.connection)
        new_type = new_db_params['type']
        if old_type is None and new_type is None and (
                old_field.remote_field and new_field.remote_field and
                old_field.remote_field.through and new_field.remote_field.through and
                old_field.remote_field.through._meta.auto_created and
                new_field.remote_field.through._meta.auto_created):
            return self._alter_many_to_many(model, old_field, new_field, strict)

    def _alter_field(self, model, old_field, new_field, old_type, new_type, old_db_params, new_db_params, strict=False):
        pass