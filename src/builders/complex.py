from .select import SelectBuilder
from .delete import DeleteBuilder
from .insert import InsertBuilder
from .update import UpdateBuilder


class WhereBuilder(SelectBuilder, DeleteBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValuesBuilder(InsertBuilder, UpdateBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
