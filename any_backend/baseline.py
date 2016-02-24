from django.test import TestCase
from importlib import import_module
import os

class BaselineTests(TestCase):
    def setUp(self):
        self.command_lists = []
        for app in self.settings().non_db_apps:
            module = import_module(app + '.testbaseline')
            self.command_lists.append({'app': app, 'commands': module.commands})

    def write(self, app, commands):
        module = os.path.dirname(app.__file__)
        file_path = os.path.join(module, 'testbaselineresults')
        with open(file_path, 'a+') as f:
            f.write(str({app: commands}))

    def test_baseline(self):
        for app, command_list in self.command_lists:
            app = command_list['app']
            commands = command_list['commands']
            for i, command in enumerate(commands):
                func = command['func']
                kwargs = command['kwargs']
                commands[i]['results'] = func(**kwargs)
            self.write(app, commands)
