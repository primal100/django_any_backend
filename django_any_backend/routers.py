from utils import backend_is_non_db, check_can_migrate, get_models_for_db, get_model_by_name

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
        model_name = hints.get('model_name', None)
        if app_label and model_name:
            model = get_model_by_name(app_label, model_name)
        if model:
            non_db = self.db_for_read(model)
            if non_db == db:
                return check_can_migrate(db)
            if not non_db and not backend_is_non_db(db):
                return True
            return False
        else:
            return True
