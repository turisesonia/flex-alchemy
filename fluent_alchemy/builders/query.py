from .select import SelectBuilder
from .delete import DeleteBuilder


class QueryBuilder(SelectBuilder, DeleteBuilder): ...
