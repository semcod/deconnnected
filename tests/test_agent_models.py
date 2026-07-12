from deconnected.agent.models import RefactorPlan, RefactorStep

def test_plan_schema_rejects_invalid_confidence():
    try:
        RefactorPlan(id="x", objective="x", confidence=2, steps=[RefactorStep(id="a", operation="x", description="x")])
        assert False
    except Exception:
        assert True

def test_default_forbidden_operations_are_safe():
    p = RefactorPlan(id="x", objective="x", steps=[])
    assert "drop_database_table" in p.forbidden_operations
    assert "push_remote" in p.forbidden_operations
