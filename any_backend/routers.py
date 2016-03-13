class BackendRouter(object):
    """
    A router to send all non-db models to the correct backend
    """
    def db_for_read(self, model, **hints):
        return getattr(model, 'non_db', None)

    def db_for_write(self, model, **hints):
        return getattr(model, 'non_db', None)

    def allow_relation(self, obj1, obj2, **hints):
        if getattr(obj1, 'non_db', None) and  getattr(obj2, 'non_db', None):
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        return True