import typing as t

from sqlalchemy import Insert, insert
from sqlalchemy.orm import Session
from sqlalchemy.engine.result import Result

from .base import BaseBuilder


class InsertBuilder(BaseBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._values = None
        self._execution_options: dict = {}
        self._returning: dict = {"cols": (), "params": {}}

    def values(self, *args, **kwargs):
        if args:
            self._values = args[0]
        else:
            self._values = kwargs

        return self

    def execution_options(self, **options):
        self._execution_options.update(options)

        return self

    def returning(self, *cols, **kwargs):
        self._returning["cols"] += (*cols,)
        self._returning["params"].update(kwargs)

        return self

    def _build(self) -> Insert:
        if not self._values:
            raise ValueError("values cannot be empty.")

        stmt = insert(self._model).values(self._values)

        if self._returning:
            stmt = stmt.returning(
                *self._returning["cols"],
                **self._returning["params"],
            )

        if self._execution_options:
            stmt = stmt.execution_options(**self._execution_options)

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
