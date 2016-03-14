from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo

class DatabaseIntrospection(BaseDatabaseIntrospection):
    def get_table_list(self, cursor):
        tables = sorted(self.connection.client.get_data().keys())
        info = [TableInfo(row, 't') for row in tables]
        return info