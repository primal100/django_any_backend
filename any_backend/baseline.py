from django.test import TestCase
from importlib import import_module
from django.conf import settings
import os

class BaselineTests(TestCase):
    def setUp(self):
        self.command_lists = []
        for app in settings.NON_DB_APPS:
            module_name = app + '.tests_baseline'
            try:
                module = import_module(app + '.tests_baseline')
                self.command_lists.append((app, module.commands))
            except ImportError:
                print('No tests_baseline module found in app: ' + app)

    def write(self, app, commands):
        module = os.path.dirname(app.__file__)
        file_path = os.path.join(module, 'testbaselineresults')
        with open(file_path, 'a+') as f:
            f.write(str({app: commands}))

    def test_baseline(self):
        for app, commands in self.command_lists:
            for i, command in enumerate(commands):
                func = command['func']
                kwargs = command['kwargs']
                commands[i]['results'] = func(**kwargs)
            self.write(app, commands)
