from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider

_ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
_SQLISH = re.compile(r"(?is)\b(select|insert|update|delete|create)\b.+\b(from|into|table|join)\b")


@dataclass
class PythonFacts:
    imports: set[str] = field(default_factory=set)
    calls: set[str] = field(default_factory=set)
    routes: list[tuple[str, str, int]] = field(default_factory=list)
    table_names: list[tuple[str, int]] = field(default_factory=list)
    sql_literals: list[tuple[str, int]] = field(default_factory=list)


class _Visitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self) -> None:
        self.facts = PythonFacts()

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            self.facts.imports.add(_name(alias.name))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is not None:
            self.facts.imports.add(_name(node.module))

    def visit_Call(self, node: cst.Call) -> None:
        self.facts.calls.add(_name(node.func))

    def visit_Assign(self, node: cst.Assign) -> None:
        value = _simple_string(node.value)
        if value is None:
            return
        for target in node.targets:
            name = _name(target.target)
            if name.endswith("__tablename__") or name.endswith("table_name"):
                line = self.get_metadata(PositionProvider, node).start.line
                self.facts.table_names.append((value, line))
        if _SQLISH.search(value):
            line = self.get_metadata(PositionProvider, node).start.line
            self.facts.sql_literals.append((value, line))

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        for decorator in node.decorators:
            expression = decorator.decorator
            if not isinstance(expression, cst.Call):
                continue
            dotted = _name(expression.func)
            method = dotted.rsplit(".", 1)[-1].lower()
            if method not in _ROUTE_METHODS or not expression.args:
                continue
            route = _simple_string(expression.args[0].value)
            if route is not None:
                line = self.get_metadata(PositionProvider, decorator).start.line
                self.facts.routes.append((method.upper(), route, line))


def analyze_python(text: str) -> PythonFacts:
    try:
        module = cst.parse_module(text)
    except cst.ParserSyntaxError:
        return PythonFacts()
    visitor = _Visitor()
    MetadataWrapper(module).visit(visitor)
    return visitor.facts


def _simple_string(node: cst.CSTNode) -> str | None:
    if isinstance(node, cst.SimpleString):
        try:
            return node.evaluated_value
        except Exception:
            return None
    return None


def _name(node: cst.CSTNode | None) -> str:
    if node is None:
        return ""
    if isinstance(node, cst.Name):
        return node.value
    if isinstance(node, cst.Attribute):
        left = _name(node.value)
        return f"{left}.{node.attr.value}" if left else node.attr.value
    return ""
