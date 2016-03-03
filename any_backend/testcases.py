from django.test import TestCase
from django.db.models.query_utils import deferred_class_factory
from django.db.models.query import get_related_populators
from collections import Counter
import six
import time

class CompareWithSQLTestCase(TestCase):
    print_times = True


    def assertQuerysetsEqual(self, qs1, qs2, transform=repr, ordered=True, msg=None):
        qs1_items = self.qs_to_list_with_time(transform, qs1)
        qs2_items = self.qs_to_list_with_time(transform, qs2)
        if not ordered:
            return self.assertEqual(Counter(qs1_items), Counter(qs2_items), msg=msg)
        qs1_values = list(qs1_items)
        qs2_values = list(qs2_items)
        self.assertEqual(qs1_values, qs2_values, msg=msg)

    def prop_with_time(self, model_table, string, obj, attr):
        result = self.run_with_time(model_table, string, getattr, obj, attr)
        return result

    def run_with_time(self, model_table, string, func, *args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        t = time.time() - startTime
        if self.print_times:
            print "%s %s %s: %.3f secs" % (self.id(), model_table, string, t)
        return result

    def save_with_time(self, model):
        startTime = time.time()
        result = model.save()
        t = time.time() - startTime
        print "%s %s save: %.3f secs" % (self.id(), model._meta.db_table, t)
        return result

    def qs_to_list_with_time(self, transform, qs):
        qs_items = self.run_with_time(qs.model._meta.db_table, 'list', six.moves.map, transform, qs)
        return qs_items

    def get_with_time(self, qs):
        result = self.run_with_time(qs.model._meta.db_table, 'get', qs.get)
        return result

    def count_with_time(self, qs):
        result = self.run_with_time(qs.model._meta.db_table, 'count', qs.count)
        return result

    def first_with_time(self, qs):
        result = self.run_with_time(qs.model._meta.db_table, 'first', qs.first)
        return result

    def last_with_time(self, qs):
        result = self.run_with_time(qs.model._meta.db_table, 'last', qs.last)
        return result

    def delete_with_time(self, qs):
        result = self.run_with_time(qs.model._meta.db_table, 'delete', qs.delete)
        return result

    def breakdown_queryset(self, queryset):
        db = queryset.db
        compiler = queryset.query.get_compiler(using=db)
        sql, params = self.run_with_time(queryset.model._meta.db_table, 'compiler.as_sql', compiler.as_sql)
        cursor = compiler.connection.cursor()
        self.run_with_time(queryset.model._meta.db_table, 'cursor.execute', cursor.execute, sql, params)
        results = []
        cursor = cursor.cursor
        cursor.results = None
        while cursor.results != []:
            if not cursor.full_request_size or cursor.pos <= cursor.full_request_size:
                cursor.query['paginator'].update(cursor.pos, cursor.size)
                cursor.results, cursor.pre_paginate_count = self.run_with_time(queryset.model._meta.db_table, 'get_results', cursor.func,
                                                                               cursor.model, cursor.params,
                                                                               **cursor.query)
                cursor.results = self.run_with_time(queryset.model._meta.db_table, 'cursor.conversion_func', cursor.conversion_func, cursor.results, cursor.fieldnames)
                cursor.full_request_size = cursor.page_size if cursor.paginated else cursor.pre_paginate_count
                if cursor.size:
                    cursor.pos += cursor.size
                else:
                    cursor.pos += cursor.pre_paginate_count + 1
                cursor.pre_paginate_count = (cursor.pre_paginate_count,)
            else:
                cursor.results = []
            results += cursor.results
        results = [results]
        select, klass_info, annotation_col_map = (compiler.select, compiler.klass_info,
                                                  compiler.annotation_col_map)
        if klass_info is None:
            return
        model_cls = klass_info['model']
        select_fields = klass_info['select_fields']
        model_fields_start, model_fields_end = select_fields[0], select_fields[-1] + 1
        init_list = [f[0].target.attname
                     for f in select[model_fields_start:model_fields_end]]
        if len(init_list) != len(model_cls._meta.concrete_fields):
            init_set = set(init_list)
            skip = [f.attname for f in model_cls._meta.concrete_fields
                    if f.attname not in init_set]
            model_cls = deferred_class_factory(model_cls, skip)
        related_populators = get_related_populators(klass_info, select, db)
        startTime = time.time()
        for row in compiler.results_iter(results):
            obj = model_cls.from_db(db, init_list, row[model_fields_start:model_fields_end])
            if related_populators:
                for rel_populator in related_populators:
                    rel_populator.populate(row, obj)
            if annotation_col_map:
                for attr_name, col_pos in annotation_col_map.items():
                    setattr(obj, attr_name, row[col_pos])

            # Add the known related objects to the model, if there are any
            if queryset._known_related_objects:
                for field, rel_objs in queryset._known_related_objects.items():
                    # Avoid overwriting objects loaded e.g. by select_related
                    if hasattr(obj, field.get_cache_name()):
                        continue
                    pk = getattr(obj, field.get_attname())
                    try:
                        rel_obj = rel_objs[pk]
                    except KeyError:
                        pass  # may happen in qs1 | qs2 scenarios
                    else:
                        setattr(obj, field.name, rel_obj)
        t = time.time() - startTime
        print "%s %s objects2models: %.3f secs" % (self.id(), queryset.model._meta.db_table, t)