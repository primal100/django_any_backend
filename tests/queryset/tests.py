from ..base import PickleDBTest


class PickleDBQuerysetTests(PickleDBTest):

    def test_qs(self):
        filters = {}
        excludes = {}
        order_by = []
        distinct = []
        single_obj = 0
        pagination = (0, 10)
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            qs1 = model1.objects.all().order_by(*order_by)
            qs2 = model2.objects.all().order_by(*order_by)
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.all().order_by(*order_by).reverse()
            qs2 = model2.objects.all().order_by(*order_by).reverse()
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.filter(**filters).order_by(*order_by)
            qs2 = model2.objects.filter(**filters).order_by(*order_by)
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.distinct(*distinct).order_by(*order_by)
            qs2 = model2.objects.distinct(*distinct).order_by(*order_by)
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.exclude(**excludes).order_by(*order_by)
            qs2 = model2.objects.exclude(**excludes).order_by(*order_by)
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.all().order_by(*order_by)[single_obj]
            qs2 = model2.objects.all().order_by(*order_by)[single_obj]
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
            qs2 = model2.objects.all().order_by(*order_by)[pagination[0]:pagination[1]]
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)
            qs1 = model1.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(
                *order_by).reverse()[pagination[0]:pagination[1]]
            qs2 = model2.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(
                *order_by).reverse()[pagination[0]:pagination[1]]
            self.assertQuerysetsEqual(qs1, qs2, **self.override_settings)

    def test_count(self):
        filters = {}
        excludes = {}
        order_by = []
        distinct = []
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            qs1 = model1.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(*order_by)
            qs2 = model2.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(*order_by)
            self.assertCountEqual(qs1, qs2, **self.override_settings)

    def test_one_results(self):
        filters = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            qs1 = model1.objects.filter(filters)
            qs2 = model2.objects.filter(filters)
            self.assertGetEqual(qs1, qs2, **self.override_settings)

    def test_multi_results(self):
        filters = {}
        excludes = {}
        order_by = []
        distinct = []
        pagination = (0, 10)
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            qs1 = model1.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(
                *order_by).reverse()[pagination[0]:pagination[1]]
            qs2 = model2.objects.filter(**filters).exclude(**excludes).distinct(*distinct).order_by(
                *order_by).reverse()[pagination[0]:pagination[1]]
            self.assertFirstEqual(qs1, qs2, **self.override_settings)
            self.assertLastEqual(qs1, qs2, **self.override_settings)
            self.assertValuesEqual(qs1, qs2, **self.override_settings)
            self.assertValueListEqual(qs1, qs2, **self.override_settings)
            self.assertExistsEqual(qs1, qs2, **self.override_settings)
            self.assertNoneEqual(qs1, qs2, **self.override_settings)

    def test_update(self):
        filters = {}
        params = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            qs1 = model1.objects.filter(**filters)
            qs2 = model2.objects.filter(**filters)
            self.assertQsUpdateEqual(qs1, qs2, params, **self.override_settings)

    def test_create_delete(self):
        params = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            self.assertQsCreateEqual(model1, model2, params, **self.override_settings)
            qs1 = model1.objects.filter(**params)
            qs2 = model2.objects.filter(**params)
            self.assertQsDeleteEqual(qs1, qs2, **self.override_settings)

    def test_bulk_create_delete(self):
        objs = {}
        filters = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            self.assertBulkCreateEqual(model1, model2, objs)
            qs1 = model1.objects.filter(**filters)
            qs2 = model2.objects.filter(**filters)
            self.assertQsDeleteEqual(qs1, qs2, **self.override_settings)

    def test_get_or_create(self):
        params = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            self.assertGetOrCreateEqual(model1, model2, params, **self.override_settings)
            self.assertGetOrCreateEqual(model1, model2, params, **self.override_settings)

    def test_update_or_create(self):
        params1 = {}
        params2 = {}
        for models in self.models_list:
            model1 = models[0]
            model2 = models[1]
            self.assertUpdateOrCreateEqual(model1, model2, params1, **self.override_settings)
            self.assertUpdateOrCreateEqual(model1, model2, params2, **self.override_settings)

    def test_annotate_aggregrate(self):
        pass