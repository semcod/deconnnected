from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

import sqlglot
from sqlglot import exp

_FALLBACK = re.compile(r'(?ix)(?:from|join|update|into|table)\s+["`]?([a-z_][\w.]*)["`]?')


@dataclass(frozen=True)
class SqlReference:
    table: str
    operation: str
    confidence: float


def extract_sql_references(sql: str, dialect: str | None = None) -> list[SqlReference]:
    """Return normalized table references from one or more SQL statements."""
    found: dict[tuple[str, str], SqlReference] = {}
    try:
        statements = sqlglot.parse(sql, read=dialect)
    except Exception:
        statements = []

    for statement in statements:
        operation = _operation(statement)
        for table in statement.find_all(exp.Table):
            name = table.name
            if not name:
                continue
            key = (name, operation)
            found[key] = SqlReference(name, operation, 0.97)

    if not found:
        for match in _FALLBACK.finditer(sql):
            name = match.group(1).split(".")[-1]
            found[(name, "unknown")] = SqlReference(name, "unknown", 0.62)
    return sorted(found.values(), key=lambda item: (item.table, item.operation))


def _operation(statement: exp.Expression) -> str:
    if isinstance(statement, exp.Select):
        return "select"
    if isinstance(statement, exp.Insert):
        return "insert"
    if isinstance(statement, exp.Update):
        return "update"
    if isinstance(statement, exp.Delete):
        return "delete"
    if isinstance(statement, exp.Create):
        return "create"
    return statement.key or "unknown"
