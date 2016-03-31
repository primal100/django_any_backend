from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property

class DatabaseFeatures(BaseDatabaseFeatures):

    @cached_property
    def supports_transactions(self):
        return False