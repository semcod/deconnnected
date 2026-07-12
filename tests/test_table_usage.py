from deconnected.model import AppGraph, Node, Edge

def test_marks_table_reachable_from_gui():
    graph = AppGraph()
    for node in [Node("gui:orders", "gui", "Orders"), Node("route:/orders", "api", "/orders"), Node("file:service.py", "code", "service.py"), Node("table:orders", "table", "orders"), Node("table:legacy", "table", "legacy")]:
        graph.add_node(node)
    graph.add_edge(Edge("gui:orders", "route:/orders", "calls", "test", 1))
    graph.add_edge(Edge("route:/orders", "file:service.py", "dispatches", "test", 1))
    graph.add_edge(Edge("file:service.py", "table:orders", "uses_table", "test", 1))
    rows = {row["table"]: row for row in graph.table_usage()}
    assert rows["orders"]["reachable_from_entrypoint"] is True
    assert rows["legacy"]["reachable_from_entrypoint"] is False
