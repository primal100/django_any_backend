from __future__ import unicode_literals
from django.test.testcases import TestCase, connections_support_transactions, call_command
from collections import Counter
from django.apps import apps
from django.db import connections
import six

class AnyBackendTestCase(TestCase):
    multi_db = True

    def setUp(self):
        self.override_settings = {}

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        if not connections_support_transactions():
            return
        cls.cls_atomics = cls._enter_atomics()

        if cls.fixtures:
            for db_name in cls._databases_names(include_mirrors=False):
                    try:
                        call_command('loaddatabulk', *cls.fixtures, **{
                            'verbosity': 0,
                            'commit': False,
                            'database': db_name,
                        })
                    except Exception:
                        cls._rollback_atomics(cls.cls_atomics)
                        raise
        try:
            cls.setUpTestData()
        except Exception:
            cls._rollback_atomics(cls.cls_atomics)
            raise

    def _fixture_setup(self):
        for db_name in self._databases_names(include_mirrors=False):
            # Reset sequences
            if self.reset_sequences:
                self._reset_sequences(db_name)

            # If we need to provide replica initial data from migrated apps,
            # then do so.
            if self.serialized_rollback and hasattr(connections[db_name], "_test_serialized_contents"):
                if self.available_apps is not None:
                    apps.unset_available_apps()
                connections[db_name].creation.deserialize_db_from_string(
                    connections[db_name]._test_serialized_contents
                )
                if self.available_apps is not None:
                    apps.set_available_apps(self.available_apps)

            if self.fixtures:
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                call_command('loaddatabulk', *self.fixtures,
                             **{'verbosity': 0, 'database': db_name})

    def assertQuerysetsEqual(self, qs1, qs2, transform=repr, ordered=True, msg=None):
        self.assertIsNotNone(qs1, msg=msg)
        self.assertIsNotNone(qs2, msg=msg)
        with self.settings(**self.override_settings):
            qs1_items = six.moves.map(transform, qs1)
            qs2_items = six.moves.map(transform, qs2)
        if not ordered:
            return self.assertEqual(Counter(qs1_items), Counter(qs2_items), msg=msg)
        qs1_values = list(qs1_items)
        qs2_values = list(qs2_items)
        self.assertEqual(qs1_values, qs2_values, msg=msg)

    def assertObjectsEqual(self, obj1, obj2, fields, msg=None):
        for field in fields:
            if type(field) == str:
                self.assertEqual(getattr(obj1, field), getattr(obj2, field), msg=msg)
            elif type(field) == dict:
                related_obj1 = getattr(obj1, field['related'])
                related_obj2 = getattr(obj2, field['related'])
                self.assertObjectsEqual(related_obj1, related_obj2, field['fields'])

    def assertAggregateEqual(self, qs1, qs2, aggregate,msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.aggregate(aggregate)
            result2 = qs2.aggregate(aggregate)
        self.assertEqual(result1, result2, msg=msg)

    def assertCountEqual(self, qs1, qs2, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.count()
            result2 = qs2.count()
        self.assertEqual(result1, result2, msg=msg)

    def assertDatesEqual(self, qs1, qs2, dates, msg=None):
        with self.settings(**self.override_settings):
            results1 = qs1.dates(*dates)
            results2 = qs2.dates(*dates)
        self.assertListEqual(results1, results2, msg=msg)

    def assertExistsEqual(self, qs1, qs2, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.exists()
            result2 = qs2.exists()
        self.assertEqual(result1, result2, msg=msg)

    def assertFirstEqual(self, qs1, qs2, fields, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.first()
            result2 = qs2.first()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertObjectsEqual(result1, result2, fields, msg=msg)

    def assertLastEqual(self, qs1, qs2, fields, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.last()
            result2 = qs2.last()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertObjectsEqual(result1, result2, fields, msg=msg)

    def assertGetEqual(self, qs1, qs2, fields, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1.get()
            result2 = qs2.get()
        self.assertObjectsEqual(result1, result2, fields, msg=msg)

    def assertOneEqual(self, qs1, qs2, index, fields, msg=None):
        with self.settings(**self.override_settings):
            result1 = qs1[index]
            result2 = qs2[index]
        self.assertObjectsEqual(result1, result2, fields, msg=msg)

    def assertSaveEqual(self, model1, model2, params1, params2, msg=None):
        result1 = self.assertSave(model1, params1, msg=msg)
        result2 = self.assertSave(model2, params2, msg=msg)
        self.assertEqual(result1, result2, msg=msg)

    def assertSaveUpdateEqual(self, qs1, qs2, params, msg=None):
        result1 = self.assertSaveUpdate(qs1, params, msg=msg)
        result2 = self.assertSaveUpdate(qs2, params, msg=msg)
        self.assertEqual(result1, result2, msg=msg)

    def assertQsCreateEqual(self, model1, model2, params1, params2, fieldnames, msg=None):
        result1 = self.assertCreate(model1, params1, msg=msg)
        result2 = self.assertCreate(model2, params2, msg=msg)
        self.assertObjectsEqual(result1, result2, fieldnames, msg=msg)

    def assertQsUpdateEqual(self, qs1, qs2, after_qs1, after_qs2, params, msg=None):
        self.assertCountEqual(qs1, qs2, msg=msg)
        self.assertCountEqual(after_qs1, after_qs2, msg=msg)
        result1 = self.assertQsUpdate(qs1, params, msg=msg)
        result2 = self.assertQsUpdate(qs2, params, msg=msg)
        self.assertEqual(result1, result2, msg=msg)
        self.assertCountEqual(qs1, qs2, msg=msg)
        self.assertCountEqual(after_qs1, after_qs2, msg=msg)

    def assertBulkCreateEqual(self, model1, model2, qs1, qs2, objs1, objs2, batch_size1=None, batch_size2=None, msg=None):
        with self.settings(**self.override_settings):
            self.assertQuerysetsEqual(qs1, qs2)
            result1 = model1.objects.bulk_create(objs1, batch_size=batch_size1)
            result2 = model2.objects.bulk_create(objs2, batch_size=batch_size2)
            self.assertQuerysetsEqual(qs1, qs2)
        self.assertEqual(str(result1), str(result2), msg=msg)

    def assertGetOrCreateEqual(self, model1, model2, params, msg=None):
        with self.settings(**self.override_settings):
            result1_obj, result1_created = model1.objects.get_or_create(**params)
            result2_obj, result2_created = model2.objects.get_or_create(**params)
        self.assertObjectsEqual(result1_obj, result2_obj, params, msg=msg)
        self.assertEqual(result1_created, result2_created, msg=msg)

    def assertUpdateOrCreateEqual(self, model1, model2, defaults, params, msg=None):
        with self.settings(**self.override_settings):
            result1_obj, result1_created = model1.objects.update_or_create(defaults=defaults, **params)
            result2_obj, result2_created = model2.objects.update_or_create(defaults=defaults, **params)
        params.update(defaults)
        self.assertObjectsEqual(result1_obj, result2_obj, params, msg=msg)
        self.assertEqual(result1_created, result2_created, msg=msg)

    def assertDeleteEqual(self, model1, model2, params, msg=None):
        result1 = self.assertDelete(model1, params, msg=msg)
        result2 = self.assertDelete(model2, params, msg=msg)
        self.assertEqual(result1[0], result2[0], msg=msg)
        self.assertEqual(result1[1].values(), result2[1].values(), msg=msg)

    def assertQsDeleteEqual(self, qs1, qs2, msg=None):
        result1 = self.assertQSDelete(qs1, msg=msg)
        result2 = self.assertQSDelete(qs2, msg=msg)
        self.assertEqual(result1[0], result2[0], msg=msg)
        self.assertEqual(result1[1].values(), result2[1].values(), msg=msg)

    def assertCreate(self, model, params, msg=None):
        with self.settings(**self.override_settings):
            result = model.objects.create(**params)
        return result

    def assertSave(self, model, params, msg=None):
        qs = model.objects.filter(**params)
        with self.settings(**self.override_settings):
            self.assertRaises(model.DoesNotExist, qs.get)
            instance = model(**params)
            result = instance.save()
            #self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def assertSaveUpdate(self, qs, params, msg=None):
        with self.settings(**self.override_settings):
            instance = qs.get()
            for k,v in params.iteritems():
                setattr(instance, k, v)
            result = instance.save()
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def assertDelete(self, model, params, msg=None):
        qs = model.objects.filter(**params)
        with self.settings(**self.override_settings):
            self.assertGreater(qs.count(), 0, msg=msg)
            instance = qs.get()
            result = instance.delete()
            self.assertRaises(instance.DoesNotExist, qs.get)
        return result

    def assertQsUpdate(self, qs, params, msg=None):
        with self.settings(**self.override_settings):
            self.assertGreater(len(qs), 0, msg=msg)
            result = qs.update(**params)
            self.assertEqual(qs.count(), 0, msg=msg)
        return result

    def assertQSDelete(self, qs, msg=None):
        with self.settings(**self.override_settings):
            self.assertGreater(len(qs), 0, msg=msg)
            result = qs.delete()
            self.assertEqual(qs.count(), 0, msg=msg)
        return result
