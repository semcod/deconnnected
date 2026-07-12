from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field

class RepositorySnapshot(BaseModel):
    commit: str
    dirty: bool
    files: dict[str, str] = Field(default_factory=dict)


def create_snapshot(repository: Path, paths: list[str] | None = None) -> RepositorySnapshot:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repository, capture_output=True, text=True, check=False).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=repository, capture_output=True, text=True, check=False).stdout.strip())
    files: dict[str, str] = {}
    candidates: list[Path] = []
    if paths:
        for item in paths:
            p = repository / item
            if p.is_file(): candidates.append(p)
            elif p.is_dir(): candidates.extend(x for x in p.rglob("*") if x.is_file())
    else:
        candidates = [x for x in repository.rglob("*") if x.is_file() and ".git" not in x.parts and ".deconnected" not in x.parts]
    for path in candidates:
        try:
            rel = path.relative_to(repository).as_posix()
            files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return RepositorySnapshot(commit=commit, dirty=dirty, files=dict(sorted(files.items())))


def diff_snapshots(before: RepositorySnapshot, after: RepositorySnapshot) -> dict:
    b, a = before.files, after.files
    return {
        "added": sorted(set(a) - set(b)),
        "removed": sorted(set(b) - set(a)),
        "modified": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
        "commit_changed": before.commit != after.commit,
    }
