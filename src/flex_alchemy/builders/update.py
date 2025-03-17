import typing as t

from sqlalchemy import Update, update
from sqlalchemy.orm import Session
from sqlalchemy.engine.result import Result

from .base import BaseWhereBuilder


class UpdateBuilder(BaseWhereBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._values: dict = {}
        self._returning: tuple = ()
        self._dialect_options: dict = {}
        self._ordered_values: tuple[tuple[str]] = ()

    def values(self, **kwargs) -> "UpdateBuilder":
        self._values.update(kwargs)

        return self

    def returning(self, *cols) -> "UpdateBuilder":
        self._returning += (*cols,)

        return self

    def with_dialect_options(self, **opts) -> "UpdateBuilder":
        self._dialect_options.update(opts)

        return self

    def ordered_values(self, *args) -> "UpdateBuilder":
        self._ordered_values += (*args,)

        return self

    def _build(self) -> Update:
        if not self._values:
            raise ValueError("values cannot be empty.")

        stmt = update(self._model).values(self._values)

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

        if self._returning:
            stmt = stmt.returning(*self._returning)

        if self._dialect_options:
            stmt = stmt.with_dialect_options(**self._dialect_options)

        if self._ordered_values:
            stmt = stmt.ordered_values(*self._ordered_values)

        return stmt

    def execute(
        self, session: t.Optional[Session] = None, commit: bool = True, *args, **kwargs
    ) -> Result[t.Any]:
        session = self.get_session(session)

        stmt = self._build()

        result = session.execute(stmt, *args, **kwargs)

        if commit:
            session.commit()

        return result
