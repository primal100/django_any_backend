from django.db.backends.base.schema import BaseDatabaseSchemaEditor

class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
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
        pass

    def remove_field(self, model, field):
        pass

    def alter_field(self, model, old_field, new_field, strict=False):
        pass

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):
        pass

    def _alter_many_to_many(self, model, old_field, new_field, strict):
        pass