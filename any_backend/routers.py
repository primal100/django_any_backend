class BackendRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read models with no_db_backend attribute go to the correct nodb_backend
        """
        meta = model._meta
        return getattr(meta, 'nodb_backend', None)

    def db_for_write(self, model, **hints):
        """
        Attempts to write models with no_db_backend attribute go to the correct nodb_backend
        """
        meta = model._meta
        return getattr(meta, 'nodb_backend', None)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a models with no_db_backend in class Meta is involved.
        """
        meta1 = obj1._meta
        meta2 = obj2._meta
        if getattr(meta1, 'no_db_backend', None) and getattr(meta2, 'no_db_backend', None):
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        if model:
            meta = model._meta
            return not getattr(meta, 'nodb_backend', None)
        else:
            return True