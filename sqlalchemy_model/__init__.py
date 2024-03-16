from .activerecord import ActiveRecord
from .mixins.timestamp import TimestampMixin
from .mixins.softdelete import SoftDeleteMixin


class AllFeature(ActiveRecord, TimestampMixin):
    pass
