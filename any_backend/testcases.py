from django.test import TestCase
from django.db.models.query_utils import deferred_class_factory
from django.db.models.query import get_related_populators
from collections import Counter
import six
import time
from django.conf import settings

class CompareWithSQLTestCase(TestCase):

    def compare_all(self, model1, model2, orderby, reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, None, None, orderby, reverse)
        self.assertQuerysetsEqual(qs1, qs2, msg=msg, **settings)

    def compare_querysets(self, model1, model2, filters=None, exclude=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, orderby, reverse)
        self.assertQuerysetsEqual(qs1, qs2, msg=msg, **settings)

    def compare_values(self, model1, model2, filters=None, exclude=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, orderby, reverse)
        with self.settings(**settings):
            results1 = qs1.values()
            results2 = qs2.values()
        self.assertDictEqual(results1, results2, msg=None)

    def compare_aggregate(self, model1, model2, aggregate, filters=None, exclude=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, orderby, reverse)
        with self.settings(**settings):
            result1 = qs1.aggregate(aggregate)
            result2 = qs2.aggregate(aggregate)
        self.assertEqual(result1, result2)

    def compare_value_lists(self, model1, model2, filters=None, exclude=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, orderby, reverse)
        with self.settings(**settings):
            results1 = qs1.value_list()
            results2 = qs2.value_list()
        self.assertListEqual(results1, results2, msg=None)

    def compare_dates(self, model1, model2, dates, filters=None, exclude=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, orderby, reverse)
        with self.settings(**settings):
            results1 = qs1.dates(*dates)
            results2 = qs2.dates(*dates)
        self.assertListEqual(results1, results2, msg=None)

    def compare_none(self, model1, model2, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, None, (), (), False)
        with self.settings(**settings):
            results1 = qs1.None()
            results2 = qs2.None()
        self.assertListEqual(results1, results2, msg=None)

    def compare_exist(self, model1, model2, filters=None, exclude=None, distinct=(), msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, None, False)
        with self.settings(**settings):
            result1 = qs1.exist()
            result2 = qs2.exist()
        self.assertEqual(result1, result2, msg=msg)

    def compare_get(self, model1, model2, filters=None, exclude=None, distinct=(), msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, exclude, distinct, None, False)
        with self.settings(**settings):
            result1 = qs1.get()
            result2 = qs2.get()
        self.assertEqual(result1, result2, msg=msg)

    def build_qs(self, model, filters, exclude, distinct, orderby, reverse):
        qs = model.objects.all()
        if filters:
            qs = model.objects.filter(**filters)
        if exclude:
            qs = qs.exclude(**exclude)
        if distinct:
            qs = qs.distinct(*distinct)
        if orderby:
            qs = model.all().orderby(*orderby)
        if reverse:
                qs = qs.reverse()
        return qs

    def build_two_qs(self, model1, model2, filters, exclude, distinct, orderby, reverse):
        qs1 =  self.build_qs(model1, filters, exclude, distinct, orderby, reverse)
        qs2 =  self.build_qs(model2, filters, exclude, distinct, orderby, reverse)
        return qs1, qs2

    def compare_first(self, model1, model2, filters=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, distinct, orderby, reverse)
        with self.settings(**settings):
            result1 = qs1.first()
            result2 = qs2.first()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2, msg=msg)

    def compare_last(self, model1, model2, filters=None, distinct=(), orderby=(), reverse=False, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, filters, distinct, orderby, reverse)
        with self.settings(**settings):
            result1 = qs1.last()
            result2 = qs2.larst()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2, msg=msg)

    def assertQuerysetsEqual(self, qs1, qs2, transform=repr, ordered=True, msg=None, **settings):
        self.assertNotEqual(qs1, None)
        self.assertNotEqual(qs2, None)
        with self.settings(**settings):
            qs1_items = six.moves.map(transform, qs1)
            qs2_items = six.moves.map(transform, qs2)
        if not ordered:
            return self.assertEqual(Counter(qs1_items), Counter(qs2_items), msg=msg)
        qs1_values = list(qs1_items)
        qs2_values = list(qs2_items)
        self.assertEqual(qs1_values, qs2_values, msg=msg)

    def compare_count(self, model1, model2, params, distinct, msg=None, **settings):
        qs1, qs2 = self.build_two_qs(model1, model2, params, distinct, (), None)
        with self.settings(**settings):
            result1 = qs1.count()
            result2 = qs2.count()
        self.assertEqual(result1, result2, msg=msg)

    def compare_save(self, model1, model2, params, msg=None, **settings):
        result1 = self.check_save(model1, params, msg=msg, **settings)
        result2 = self.check_save(model2, params, msg=msg, **settings)
        self.assertEqual(result1, result2)
        self.compare_get(model1, model2, filters=params, msg=msg, **settings)

    def compare_create(self, model1, model2, params, msg=None, **settings):
        result1 = self.check_create(model1, params, msg=msg, **settings)
        result2 = self.check_create(model2, params, msg=msg, **settings)
        self.assertEqual(result1, result2)
        self.compare_get(model1, model2, filters=params, msg=msg, **settings)

    def compare_update(self, model1, model2, params, filters=None, distinct=(), msg=None, **settings):
        result1 = self.check_update(model1, params, filters=filters, distinct=distinct, msg=msg, **settings)
        result2 = self.check_update(model2, params, filters=filters, distinct=distinct, msg=msg, **settings)
        self.assertEqual(result1, result2)
        filters.update(params)
        self.compare_get(model1, model2, filters=filters, distinct=distinct, msg=None, **settings)

    def compare_bulk_create(self, model1, model2, objs, batch_size1=None, batch_size2=None, msg=None **settings):
        with self.settings(**settings):
            result1 = model1.objects.bulk_create(objs, batch_size=batch_size1)
            result2 = model2.objects.bulk_create(objs, batch_size=batch_size2)
        self.assertEqual(result1, result2)
        for obj in objs:
            self.compare_get(model1, model2, filters=obj, msg=msg, **settings)


    def compare_update_or_create(self, model1, model2, params, msg=None, **settings):
        with self.settings(**settings):
            result1_obj, result1_created = model1.objects.update_or_create(**params)
            result2_obj, result2_created = model2.objects.update_or_create(**params)
        self.assertEqual(result1_obj, result2_obj)
        self.assertEqual(result1_created, result2_created)

    def compare_delete(self, model1, model2, filters=None, distinct=(), msg=None, **settings):
        result1 = self.check_delete(model1, filters=filters, distinct=distinct, msg=msg, **settings)
        result2 = self.check_delete(model2, filters=filters, distinct=distinct, msg=msg, **settings)
        self.assertEqual(result1, result2, msg=msg)

    def check_create(self, model, params, msg=None, **settings):
        qs = self.build_qs(model, params, (), None, False)
        with self.settings(**settings):
            self.assertRaises(qs.get(), model.DoesNotExist, msg=msg)
            result = model.objects.create(**params)
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def compare_get_or_create(self, model1, model2, params, msg=None, **settings):
        with self.settings(**settings):
            result1_obj, result1_created = model1.objects.get_or_create(**params)
            result2_obj, result2_created = model2.objects.get_or_create(**params)
        self.assertEqual(result1_obj, result2_obj)
        self.assertEqual(result1_created, result2_created)

    def check_save(self, model, params, msg=None, **settings):
        qs = self.build_qs(model, params, (), None, False)
        with self.settings(**settings):
            self.assertRaises(qs.get(), model.DoesNotExist, msg=msg)
            instance = model(**params)
            result = instance.save()
            self.assertGreater(qs.count(), 0, msg=msg)
        return result

    def check_update(self, model, params, filters=None, distinct=(), msg=None, **settings):
        qs = self.build_qs(model, filters, distinct, None, False)
        with self.settings(**settings):
            self.assertGreater(len(qs), 0, msg=msg)
            result = qs.update(**params)
            filters.update(params)
            qs = self.build_qs(model, filters, distinct, None, False)
            self.assertGreater(qs.count(), 0)
        return result

    def check_delete(self, model, filters=None, distinct=(), msg=None, **settings):
        qs = self.build_qs(model, filters, distinct, None, False)
        self.assertGreater(qs.count(), 0, msg=msg)
        with self.settings(**settings):
            result = qs.delete()
            self.assertRaises(qs.get(), model.DoesNotExist, msg=msg)
        return result
