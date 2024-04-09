from .select import SelectBuilder
from .delete import DeleteBuilder
from .insert import InsertBuilder


class QueryBuilder(SelectBuilder, DeleteBuilder, InsertBuilder): ...
