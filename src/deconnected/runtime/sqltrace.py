from __future__ import annotations
import re
from sqlalchemy import event
from sqlalchemy.engine import Engine

SQL_TABLE = re.compile(r'(?ix)(?:from|join|update|into)\s+["`]?([a-z_][\w.]*)["`]?')

class SqlTrace:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.statements: list[str] = []
        self.tables: set[str] = set()

    def _before(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(statement)
        self.tables.update(match.group(1).split(".")[-1] for match in SQL_TABLE.finditer(statement))

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self._before)
        return self

    def __exit__(self, exc_type, exc, tb):
        event.remove(self.engine, "before_cursor_execute", self._before)
