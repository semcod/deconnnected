from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

class WorktreeManager:
    def __init__(self, repository: Path, base_dir: Path | None = None):
        self.repository = repository.resolve()
        self.base_dir = (base_dir or self.repository / ".deconnected" / "worktrees").resolve()

    def create(self, run_id: str) -> Path:
        target = self.base_dir / run_id
        target.parent.mkdir(parents=True, exist_ok=True)
        branch = f"deconnected/{run_id}"
        result = subprocess.run(["git", "worktree", "add", "-b", branch, str(target)], cwd=self.repository, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return target

    def remove(self, target: Path, force: bool = False) -> None:
        args = ["git", "worktree", "remove"] + (["--force"] if force else []) + [str(target)]
        result = subprocess.run(args, cwd=self.repository, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
