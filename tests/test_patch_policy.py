import subprocess
from pathlib import Path
from deconnected.agent.models import RefactorPlan, RefactorStep
from deconnected.refactor.policy import evaluate_patch_policy


def _git(repo: Path, *args: str):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x=1\n")
    (tmp_path / "README.md").write_text("ok\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "init")
    return tmp_path


def _plan(paths):
    return RefactorPlan(id="x", objective="x", steps=[RefactorStep(id="s", operation="edit", description="x")], allowed_paths=paths)


def test_policy_allows_in_scope_change(tmp_path):
    repo = _repo(tmp_path)
    (repo / "src" / "a.py").write_text("x=2\n")
    report = evaluate_patch_policy(repo, _plan(["src"]))
    assert report.passed
    assert report.changed_files == ["src/a.py"]


def test_policy_blocks_out_of_scope_change(tmp_path):
    repo = _repo(tmp_path)
    (repo / "README.md").write_text("changed\n")
    report = evaluate_patch_policy(repo, _plan(["src"]))
    assert not report.passed
    assert report.findings[0].code == "scope_violation"


def test_policy_blocks_drop_table(tmp_path):
    repo = _repo(tmp_path)
    (repo / "src" / "a.py").write_text('op.drop_table("users")\n')
    report = evaluate_patch_policy(repo, _plan(["src"]))
    assert not report.passed
    assert any(x.code == "forbidden:drop_database_table" for x in report.findings)
