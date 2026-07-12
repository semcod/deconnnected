from deconnected.frontend_tests import generate_frontend_checks, render_testql_scenario
from deconnected.model import AppGraph, Node


def test_generates_deduplicated_page_and_asset_checks():
    graph = AppGraph()
    graph.add_node(Node("p", "gui", "http://localhost:8100"))
    graph.add_node(Node("a1", "asset", "http://localhost:8100/main.js"))
    graph.add_node(Node("a2", "asset", "http://localhost:8100/main.js"))
    checks = generate_frontend_checks(graph)
    assert len(checks) == 2
    scenario = render_testql_scenario(checks)
    assert "API[2]" in scenario
    assert "GET, /main.js, 200" in scenario
