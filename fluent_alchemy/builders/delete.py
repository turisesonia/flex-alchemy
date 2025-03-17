import typing as t

from sqlalchemy import delete, Delete
from sqlalchemy.orm import Session
from sqlalchemy.engine.result import Result


from .base import BaseWhereBuilder


class DeleteBuilder(BaseWhereBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _build(self) -> Delete:
        stmt = delete(self._model)

        if self._where_clauses:
            stmt = stmt.where(*self._where_clauses)

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
