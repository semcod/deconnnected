from __future__ import annotations
import fnmatch
import re
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from deconnected.agent.models import RefactorPlan

class PolicyFinding(BaseModel):
    code: str
    severity: str
    message: str
    path: str | None = None

class PolicyReport(BaseModel):
    passed: bool
    changed_files: list[str] = Field(default_factory=list)
    findings: list[PolicyFinding] = Field(default_factory=list)


def _changed_files(repository: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=repository,
        capture_output=True, text=True, check=False,
    )
    return sorted({line.strip() for line in proc.stdout.splitlines() if line.strip()})


def _allowed(path: str, patterns: list[str]) -> bool:
    if not patterns:
        return False
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        p = pattern.replace("\\", "/").rstrip("/")
        if normalized == p or normalized.startswith(p + "/") or fnmatch.fnmatch(normalized, p):
            return True
    return False


def evaluate_patch_policy(repository: Path, plan: RefactorPlan) -> PolicyReport:
    changed = _changed_files(repository)
    findings: list[PolicyFinding] = []
    for path in changed:
        if not _allowed(path, plan.allowed_paths):
            findings.append(PolicyFinding(
                code="scope_violation", severity="error",
                message="File changed outside plan.allowed_paths", path=path,
            ))

    diff = subprocess.run(
        ["git", "diff", "--unified=0", "HEAD"], cwd=repository,
        capture_output=True, text=True, check=False,
    ).stdout
    checks = {
        "drop_database_table": r"(?im)^\+.*\b(?:DROP\s+TABLE|op\.drop_table\s*\()",
        "rewrite_public_api": r"(?im)^[-+].*(?:@(?:app|router)\.(?:get|post|put|patch|delete)|path\s*\(|router\.(?:get|post|put|patch|delete))",
        "delete_git_history": r"(?im)^\+.*(?:git\s+(?:reset\s+--hard|rebase|filter-branch)|rm\s+-rf\s+\.git)",
        "push_remote": r"(?im)^\+.*git\s+push\b",
    }
    for operation in plan.forbidden_operations:
        pattern = checks.get(operation)
        if pattern and re.search(pattern, diff):
            findings.append(PolicyFinding(
                code=f"forbidden:{operation}", severity="error",
                message=f"Patch appears to perform forbidden operation: {operation}",
            ))
    return PolicyReport(passed=not findings, changed_files=changed, findings=findings)
