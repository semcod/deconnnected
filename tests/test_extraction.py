from deconnected.analysis import extraction_candidates
from deconnected.model import AppGraph, Edge, Node


def test_extraction_candidates_uses_connected_components():
    graph = AppGraph()
    graph.add_node(Node("a", "code", "a"))
    graph.add_node(Node("b", "code", "b"))
    graph.add_edge(Edge("a", "b", "imports", "x"))
    candidates = extraction_candidates(graph)
    assert candidates[0]["size"] == 2
