from .activerecord import ActiveRecord
from .mixins.timestamp import TimestampMixin


class AllFeature(ActiveRecord, TimestampMixin):
    pass
