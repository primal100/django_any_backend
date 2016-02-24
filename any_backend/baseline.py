from django.test import TestCase
from importlib import import_module

class BaselineTests(TestCase):
    def setUp(self):
        self.command_lists = []
        for app in self.settings().non_db_apps:
            module = import_module(app + '.testbaseline')
            self.command_lists.append(module.commands)

    def write(self, app, commands):
        pass

    def test_baseline(self):
        for app, commands in enumerate(self.command_lists).iteritems():
            for i, command in enumerate(commands):
                func = command['func']
                kwargs = command['kwargs']
                commands[i]['results'] = func(**kwargs)
            self.write(app, commands)
