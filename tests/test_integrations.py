from pathlib import Path
from deconnected.integrations.runner import SPECS, available_integrations, run_integration


def test_expected_ecosystem_integrations_are_registered():
    assert {"testql", "code2llm", "code2logic", "redup", "regix", "vallm", "toonic"} <= set(SPECS)


def test_missing_tool_is_reported_without_crashing(tmp_path, monkeypatch):
    monkeypatch.setattr("deconnected.integrations.runner._available", lambda spec: False)
    result = run_integration("redup", tmp_path, tmp_path / "out")
    assert result.status == "missing"
    assert result.available is False


def test_availability_has_purpose():
    rows = available_integrations()
    assert all(row["purpose"] for row in rows)
