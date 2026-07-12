from deconnected.correlation import correlate_runtime_to_routes
from deconnected.model import AppGraph, Node


def test_correlates_runtime_url_with_static_parameter_route():
    graph = AppGraph()
    graph.add_node(Node("route:/api/orders/{id}", "api", "/api/orders/{id}"))
    graph.add_node(Node("url:http://localhost/api/orders/42", "api", "http://localhost/api/orders/42"))
    assert correlate_runtime_to_routes(graph) == 1
    assert graph.graph.has_edge("url:http://localhost/api/orders/42", "route:/api/orders/{id}")
