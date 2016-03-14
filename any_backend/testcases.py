from django.test import TestCase
from collections import Counter
import six
from django.conf import settings

class CompareWithSQLTestCase(TestCase):

    def setUp(self):
        self.override_settings = {}

    def assertQuerysetsEqual(self, qs1, qs2, transform=repr, ordered=True, msg=None, **settings):
        self.assertIsNotNone(qs1, msg=msg)
        self.assertIsNotNone(qs2, msg=msg)
        with self.settings(**settings):
            qs1_items = six.moves.map(transform, qs1)
            qs2_items = six.moves.map(transform, qs2)
        if not ordered:
            return self.assertEqual(Counter(qs1_items), Counter(qs2_items), msg=msg)
        qs1_values = list(qs1_items)
        qs2_values = list(qs2_items)
        self.assertEqual(qs1_values, qs2_values, msg=msg)

    def assertValuesEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            results1 = qs1.values()
            results2 = qs2.values()
        self.assertDictEqual(results1, results2, msg=msg)

    def assertValueListEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            results1 = qs1.value_list()
            results2 = qs2.value_list()
        self.assertListEqual(results1, results2, msg=msg)

    def assertAggregateEqual(self, qs1, qs2, aggregate,msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.aggregate(aggregate)
            result2 = qs2.aggregate(aggregate)
        self.assertEqual(result1, result2, msg=msg)

    def assertCountEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.count()
            result2 = qs2.count()
        self.assertEqual(result1, result2, msg=msg)

    def assertDatesEqual(self, qs1, qs2, dates, msg=None, **settings):
        with self.settings(**settings):
            results1 = qs1.dates(*dates)
            results2 = qs2.dates(*dates)
        self.assertListEqual(results1, results2, msg=msg)

    def assertExistsEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.exist()
            result2 = qs2.exist()
        self.assertEqual(result1, result2, msg=msg)

    def assertFirstEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.first()
            result2 = qs2.first()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2, msg=msg)

    def assertLastEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.last()
            result2 = qs2.larst()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2, msg=msg)

    def assertGetEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            result1 = qs1.get()
            result2 = qs2.get()
        self.assertEqual(result1, result2, msg=msg)

    def assertNoneEqual(self, qs1, qs2, msg=None, **settings):
        with self.settings(**settings):
            results1 = qs1.None()
            results2 = qs2.None()
        self.assertListEqual(results1, results2, msg=msg)

    def assertSaveEqual(self, model1, model2, params, msg=None, **settings):
        result1 = self.assertSave(model1, params, msg=msg, **settings)
        result2 = self.assertSave(model2, params, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)
        self.assertGetEqual(model1, model2, filters=params, msg=msg, **settings)

    def assertSaveUpdateEqual(self, qs1, qs2, params, msg=None, **settings):
        result1 = self.assertSaveUpdate(qs1, params, msg=msg, **settings)
        result2 = self.assertSaveUpdate(qs2, params, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)
        self.assertGetEqual(qs1, qs2, filters=params, msg=msg, **settings)

    def assertQsCreateEqual(self, model1, model2, params, msg=None, **settings):
        result1 = self.assertCreate(model1, params, msg=msg, **settings)
        result2 = self.assertCreate(model2, params, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)
        self.assertGetEqual(model1, model2, filters=params, msg=msg, **settings)

    def assertQsUpdateEqual(self, qs1, qs2, params, msg=None, **settings):
        result1 = self.assertQsUpdate(qs1, params, msg=msg, **settings)
        result2 = self.assertQsUpdate(qs2, params, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)
        self.assertGetEqual(qs1.count(), qs2.count(), msg=msg, **settings)

    def assertBulkCreateEqual(self, model1, model2, objs1, objs2, batch_size1=None, batch_size2=None, msg=None, **settings):
        with self.settings(**settings):
            result1 = model1.objects.bulk_create(objs1, batch_size=batch_size1)
            result2 = model2.objects.bulk_create(objs2, batch_size=batch_size2)
        self.assertEqual(result1, result2, msg=msg)
        """for obj in objs1:
            self.assertGetEqual(model1, model2, filters=obj, msg=msg, **settings)"""

    def assertGetOrCreateEqual(self, model1, model2, params, msg=None, **settings):
        with self.settings(**settings):
            result1_obj, result1_created = model1.objects.get_or_create(**params)
            result2_obj, result2_created = model2.objects.get_or_create(**params)
        self.assertEqual(result1_obj, result2_obj, msg=msg)
        self.assertEqual(result1_created, result2_created, msg=msg)

    def assertUpdateOrCreateEqual(self, model1, model2, defaults, params, msg=None, **settings):
        with self.settings(**settings):
            result1_obj, result1_created = model1.objects.update_or_create(defaults=defaults, **params)
            result2_obj, result2_created = model2.objects.update_or_create(defaults=defaults, **params)
        self.assertEqual(result1_obj, result2_obj, msg=msg)
        self.assertEqual(result1_created, result2_created, msg=msg)

    def assertDeleteEqual(self, model1, model2, params, msg=None, **settings):
        result1 = self.assertDelete(model1, params, msg=msg, **settings)
        result2 = self.assertDelete(model2, params, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)

    def assertQsDeleteEqual(self, model1, model2, filters=None, distinct=(), msg=None, **settings):
        result1 = self.assertQSDelete(model1, filters=filters, distinct=distinct, msg=msg, **settings)
        result2 = self.assertQSDelete(model2, filters=filters, distinct=distinct, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)

    def assertCreate(self, model, params, msg=None, **settings):
        qs = model.objects.filter(**params)
        with self.settings(**settings):
            self.assertRaises(qs.get(), model.DoesNotExist, msg=msg)
            result = model.objects.create(**params)
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def assertSave(self, model, params, msg=None, **settings):
        qs = model.objects.filter(**params)
        with self.settings(**settings):
            self.assertRaises(qs.get(), model.DoesNotExist, msg=msg)
            instance = model(**params)
            result = instance.save()
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def assertSaveUpdate(self, qs, params, msg=None, **settings):
        with self.settings(**settings):
            instance = qs.get()
            for k,v in params.iteritems():
                setattr(instance, k, v)
            result = instance.save()
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def assertDelete(self, qs, msg=None, **settings):
        with self.settings(**settings):
            self.assertGreater(qs.count(), 0, msg=msg)
            instance = qs.get()
            result = instance.delete()
            self.assertRaises(qs.get(), instance.DoesNotExist, msg=msg)
        return result

    def assertQsUpdate(self, qs, params, msg=None, **settings):
        with self.settings(**settings):
            self.assertGreater(len(qs), 0, msg=msg)
            result = qs.update(**params)
            self.assertEqual(qs.count(), 0, msg=msg)
        return result

    def assertQSDelete(self, qs, msg=None, **settings):
        with self.settings(**settings):
            self.assertGreater(qs.count(), 0, msg=msg)
            result = qs.delete()
            self.assertEqual(qs.count(), 0, msg=msg)
        return result
