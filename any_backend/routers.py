from utils import backend_is_non_db, get_db_for_model

class BackendRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read models with no_db_backend attribute go to the correct nodb_backend
        """
        return get_db_for_model(model)

    def db_for_write(self, model, **hints):
        """
        Attempts to write models with no_db_backend attribute go to the correct nodb_backend
        """
        return get_db_for_model(model)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a models with no_db_backend in class Meta is involved.
        """
        if get_db_for_model(obj1) and get_db_for_model(obj2):
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        return not backend_is_non_db(db)