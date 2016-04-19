from django.apps import AppConfig, apps
from django.db import router
from django.conf import settings
from django.utils.module_loading import import_string


class AnyBackendConfig(AppConfig):

    def ready(self):
        for db in settings.DATABASES:
            name = db['NAME']
            db_wrapper_class = import_string(db['ENGINE'] + '.base.DatabaseWrapper')
            base_model = getattr(db_wrapper_class, 'base_model', None)
            if base_model:
                models = apps.get_models()
                for model in models:
                    if name == router.db_for_read(model):
                        for k, v in base_model.__dict__:
                            if k == 'objects':
                                model_manager = getattr(model, 'objects', None)
                                if model_manager:
                                    manager_cls = model_manager.__class__
                                    custom_cls = v.__class__
                                    new_manager = type('AnyBackendCustomManager', (custom_cls, manager_cls), {})
                                    setattr(model, 'objects', new_manager())
                                else:
                                    setattr(model, 'objects', v)
                            elif not k.startswith('__'):
                                setattr(model, k ,v)


