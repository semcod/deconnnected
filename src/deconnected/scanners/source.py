from __future__ import annotations

import re
from pathlib import Path

from deconnected.model import AppGraph, Edge, Node
from deconnected.python_analysis import analyze_python
from deconnected.sql_analysis import extract_sql_references

API_PATTERNS = [
    re.compile(r'''(?x)\bfetch\s*\(\s*["'`]([^"'`]+)'''),
    re.compile(r'''(?x)\baxios\.(?:get|post|put|patch|delete)\s*\(\s*["'`]([^"'`]+)'''),
]
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".sql", ".php", ".go", ".java", ".kt"}
IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".deconnected"}


def _kind(path: Path) -> str:
    value = f"/{path.as_posix().lower()}"
    if "test" in path.name.lower() or "/tests/" in value:
        return "test"
    if path.suffix in {".tsx", ".jsx", ".vue", ".html"} or "/frontend/" in value:
        return "gui"
    if "route" in value or "controller" in value or "/api/" in value:
        return "api"
    if "worker" in value or "job" in value or "task" in value:
        return "job"
    if "script" in value or path.name == "manage.py":
        return "cli"
    return "code"


def scan_source(root: Path) -> AppGraph:
    graph = AppGraph()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORE for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        file_id = f"file:{rel}"
        kind = _kind(path)
        graph.add_node(Node(file_id, kind, rel, rel))
        text = path.read_text(encoding="utf-8", errors="ignore")

        if path.suffix == ".py":
            _scan_python(graph, file_id, rel, kind, text)
        if path.suffix == ".sql":
            _add_sql(graph, file_id, rel, kind, text, 1)
        else:
            _scan_embedded_sql(graph, file_id, rel, kind, text)
        _scan_frontend_calls(graph, file_id, rel, kind, text)
    return graph


def _scan_python(graph: AppGraph, file_id: str, rel: str, kind: str, text: str) -> None:
    facts = analyze_python(text)
    for module in facts.imports:
        module_id = f"module:{module}"
        graph.add_node(Node(module_id, "module", module))
        graph.add_edge(Edge(file_id, module_id, "imports", rel, 0.96, test_only=(kind == "test")))
    for method, route, line in facts.routes:
        route_id = f"route:{route}"
        graph.add_node(Node(route_id, "api", route, metadata={"method": method}))
        graph.add_edge(Edge(route_id, file_id, "implemented_by", f"{rel}:{line}", 0.98,
                            test_only=(kind == "test")))
    for table, line in facts.table_names:
        _add_table_edge(graph, file_id, table, "declares_table", f"{rel}:{line}", 0.98, kind)
    for sql, line in facts.sql_literals:
        _add_sql(graph, file_id, rel, kind, sql, line)


def _scan_embedded_sql(graph: AppGraph, file_id: str, rel: str, kind: str, text: str) -> None:
    for match in re.finditer(r'''(?is)(["'`]{1,3})(.*?\b(?:select|insert|update|delete)\b.*?)(?:\1)''', text):
        line = text.count("\n", 0, match.start()) + 1
        _add_sql(graph, file_id, rel, kind, match.group(2), line)


def _add_sql(graph: AppGraph, file_id: str, rel: str, kind: str, sql: str, line: int) -> None:
    for ref in extract_sql_references(sql):
        _add_table_edge(graph, file_id, ref.table, "uses_table",
                        f"{rel}:{line} operation={ref.operation}", ref.confidence, kind)


def _add_table_edge(graph: AppGraph, file_id: str, table: str, edge_kind: str,
                    evidence: str, confidence: float, source_kind: str) -> None:
    normalized = table.split(".")[-1]
    table_id = f"table:{normalized}"
    graph.add_node(Node(table_id, "table", normalized))
    graph.add_edge(Edge(file_id, table_id, edge_kind, evidence, confidence,
                        test_only=(source_kind == "test")))


def _scan_frontend_calls(graph: AppGraph, file_id: str, rel: str, kind: str, text: str) -> None:
    for pattern in API_PATTERNS:
        for match in pattern.finditer(text):
            route = match.group(1)
            route_id = f"route:{route}"
            graph.add_node(Node(route_id, "api", route))
            graph.add_edge(Edge(file_id, route_id, "calls_api", rel, 0.82,
                                test_only=(kind == "test")))
