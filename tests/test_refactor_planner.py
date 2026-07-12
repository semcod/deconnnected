from deconnected.model import AppGraph, Node, Edge
from deconnected.refactor.planner import build_rule_based_plan

def test_build_plan_contains_checkpoint_and_validation():
    g = AppGraph()
    g.add_node(Node("gui:x", "gui", "x", "frontend/x.js"))
    g.add_node(Node("file:a", "code", "a", "backend/a.py"))
    g.add_edge(Edge("gui:x", "file:a", "calls", "test", 1))
    p = build_rule_based_plan(g, "extract x")
    assert p.steps[0].operation == "create_checkpoint"
    assert p.validations
    assert "drop_database_table" in p.forbidden_operations
