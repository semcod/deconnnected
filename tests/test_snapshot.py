import subprocess
from deconnected.refactor.snapshot import create_snapshot, diff_snapshots


def test_snapshot_diff(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True)
    p = tmp_path / "a.txt"
    p.write_text("a")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "i"], cwd=tmp_path, check=True, capture_output=True)
    before = create_snapshot(tmp_path)
    p.write_text("b")
    (tmp_path / "b.txt").write_text("x")
    after = create_snapshot(tmp_path)
    diff = diff_snapshots(before, after)
    assert diff["modified"] == ["a.txt"]
    assert diff["added"] == ["b.txt"]
