from django.core.management.commands.dumpdata import Command as BaseDumpDataCommand
from django.apps import apps
from django.core import serializers
from django.core.management.base import CommandError
from collections import OrderedDict

class Command(BaseDumpDataCommand):
    help = ("Output the contents of the non-db backend as a fixture of the given "
            "format (using each model's default manager unless --all is "
            "specified).")

    def handle(self, *app_labels, **options):
        format = options.get('format')
        indent = options.get('indent')
        excludes = options.get('exclude')
        output = options.get('output')
        show_traceback = options.get('traceback')
        use_natural_foreign_keys = options.get('use_natural_foreign_keys')
        use_natural_primary_keys = options.get('use_natural_primary_keys')
        use_base_manager = options.get('use_base_manager')
        pks = options.get('primary_keys')

        if pks:
            primary_keys = pks.split(',')
        else:
            primary_keys = []

        excluded_apps = set()
        excluded_models = set()
        for exclude in excludes:
            if '.' in exclude:
                try:
                    model = apps.get_model(exclude)
                except LookupError:
                    raise CommandError('Unknown model in excludes: %s' % exclude)
                excluded_models.add(model)
            else:
                try:
                    app_config = apps.get_app_config(exclude)
                except LookupError as e:
                    raise CommandError(str(e))
                excluded_apps.add(app_config)

        if len(app_labels) == 0:
            if primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict((app_config, None)
                for app_config in apps.get_app_configs()
                if app_config.models_module is not None and app_config not in excluded_apps)
        else:
            if len(app_labels) > 1 and primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict()
            for label in app_labels:
                try:
                    app_label, model_label = label.split('.')
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    try:
                        model = app_config.get_model(model_label)
                    except LookupError:
                        raise CommandError("Unknown model: %s.%s" % (app_label, model_label))

                    app_list_value = app_list.setdefault(app_config, [])

                    # We may have previously seen a "all-models" request for
                    # this app (no model qualifier was given). In this case
                    # there is no need adding specific models to the list.
                    if app_list_value is not None:
                        if model not in app_list_value:
                            app_list_value.append(model)
                except ValueError:
                    if primary_keys:
                        raise CommandError("You can only use --pks option with one model")
                    # This is just an app - no model qualifier
                    app_label = label
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    app_list[app_config] = None

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            try:
                serializers.get_serializer(format)
            except serializers.SerializerDoesNotExist:
                pass

            raise CommandError("Unknown serialization format: %s" % format)

        def get_objects(count_only=False):
            """
            Collate the objects to be serialized. If count_only is True, just
            count the number of objects to be serialized.
            """
            for model in serializers.sort_dependencies(app_list.items()):
                if model in excluded_models:
                    continue
                if not model._meta.proxy:
                    if use_base_manager:
                        objects = model._base_manager
                    else:
                        objects = model._default_manager
                    queryset = objects.order_by(model._meta.pk.name)
                    if primary_keys:
                        queryset = queryset.filter(pk__in=primary_keys)
                    if count_only:
                        yield queryset.order_by().count()
                    else:
                        for obj in queryset.iterator():
                            yield obj

        try:
            self.stdout.ending = None
            progress_output = None
            object_count = 0
            # If dumpdata is outputting to stdout, there is no way to display progress
            if (output and self.stdout.isatty() and options['verbosity'] > 0):
                progress_output = self.stdout
                object_count = sum(get_objects(count_only=True))
            stream = open(output, 'w') if output else None
            try:
                serializers.serialize(format, get_objects(), indent=indent,
                        use_natural_foreign_keys=use_natural_foreign_keys,
                        use_natural_primary_keys=use_natural_primary_keys,
                        stream=stream or self.stdout, progress_output=progress_output,
                        object_count=object_count)
            finally:
                if stream:
                    stream.close()
        except Exception as e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize non-db-backend: %s" % e)