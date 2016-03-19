from __future__ import unicode_literals
from django.core.management.commands.loaddata import humanize, CommandError, Command as BaseLoadCommand
from django.core import serializers
from django.db import DatabaseError, IntegrityError, router
from django.utils.encoding import force_text
from collections import OrderedDict
import warnings
import os

class Command(BaseLoadCommand):

    def load_label(self, fixture_label):
        """
        Loads fixtures files for a given label using the queryset's bulk_create method.
        """
        show_progress = self.verbosity >= 3
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            try:
                self.fixture_count += 1
                objects_in_fixture = 0
                loaded_objects_in_fixture = 0
                if self.verbosity >= 2:
                    self.stdout.write("Installing %s fixture '%s' from %s." %
                        (ser_fmt, fixture_name, humanize(fixture_dir)))

                objects = serializers.deserialize(ser_fmt, fixture,
                    using=self.using, ignorenonexistent=self.ignore)

                create_dict = OrderedDict()

                for object in objects:
                    obj = object.object
                    objects_in_fixture += 1
                    model = obj.__class__
                    if router.allow_migrate_model(self.using, model):
                        self.models.add(model)
                        if model in create_dict.keys():
                            create_dict[model].append(obj)
                        else:
                            create_dict[model] = [obj]
                for model in create_dict.keys():
                    objs = create_dict[model]
                    loaded_objects_in_fixture += len(objs)
                    try:
                        model.objects.using(self.using).bulk_create(objs)
                        if show_progress:
                            self.stdout.write(
                                '\rProcessed %i object(s).' % loaded_objects_in_fixture,
                                ending=''
                                )
                    except (DatabaseError, IntegrityError) as e:
                        e.args = ("Could not load %(app_label)s.%(object_name)s: %(error_msg)s" % {
                                'app_label': model._meta.app_label,
                                'object_name': model._meta.object_name,
                                'error_msg': force_text(e)
                        },)
                        raise
                if objects and show_progress:
                    self.stdout.write('')  # add a newline after progress indicator
                self.loaded_object_count += loaded_objects_in_fixture
                self.fixture_object_count += objects_in_fixture
            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = ("Problem installing fixture '%s': %s" % (fixture_file, e),)
                raise
            finally:
                fixture.close()

            # Warn if the fixture we loaded contains 0 objects.
            if objects_in_fixture == 0:
                warnings.warn(
                    "No fixture data found for '%s'. (File format may be "
                    "invalid.)" % fixture_name,
                    RuntimeWarning
                )