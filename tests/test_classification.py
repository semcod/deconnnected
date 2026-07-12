from deconnected.classification import classify_tables
from deconnected.model import AppGraph, Edge, Node


def test_classifies_runtime_and_probable_legacy_tables():
    graph = AppGraph()
    graph.add_node(Node("route:/orders", "api", "/orders"))
    graph.add_node(Node("file:repo.py", "code", "repo.py"))
    graph.add_node(Node("table:orders", "table", "orders"))
    graph.add_node(Node("table:legacy", "table", "legacy"))
    graph.add_edge(Edge("route:/orders", "file:repo.py", "implemented_by", "x", 1.0))
    graph.add_edge(Edge("file:repo.py", "table:orders", "sql_select", "x", 1.0, runtime=True))
    rows = {row["label"]: row for row in classify_tables(graph)}
    assert rows["orders"]["classification"] == "actively_used"
    assert rows["orders"]["removable"] is False
    assert rows["legacy"]["classification"] == "probable_legacy"
    assert rows["legacy"]["removable"] is True
