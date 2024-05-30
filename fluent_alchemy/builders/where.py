from .select import SelectBuilder
from .delete import DeleteBuilder


class WhereBuilder(SelectBuilder, DeleteBuilder):
    def __init__(self, *args, **kwargs):
        super(WhereBuilder, self).__init__(*args, **kwargs)
