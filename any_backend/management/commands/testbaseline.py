from django.core.management.commands.test import Command as TestCommand
from any_backend.utils import backend_is_non_db
import os
import sys

class Command(TestCommand):
    help = 'Generates a baseline of test results using sqlite to later compare with a non_db backend'

    def handle(self, *test_labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner
        test_labels = ['any_backend.baseline']
        apps = []
        for i, database in enumerate(settings.DATABASES):
            if backend_is_non_db(database):
                models = database.MODELS
                for model in models:
                    app = model.split('_')[0]
                    if app not in apps:
                        apps.append(app)
                settings.DATABASES[i].ENGINE = 'django.db.backends.sqlite3'
                if 'TEST' in settings.DATABASE[i].keys():
                    del settings.DATABASE[i].TEST

        settings.nondb_apps = apps

        TestRunner = get_runner(settings, options.get('testrunner'))

        if options.get('liveserver') is not None:
            os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options['liveserver']
            del options['liveserver']

        test_runner = TestRunner(**options)
        failures = test_runner.run_tests(test_labels)

        if failures:
            sys.exit(bool(failures))

