from __future__ import annotations
import subprocess
import time
from pathlib import Path
from pydantic import BaseModel, Field
from deconnected.agent.models import ValidationStep

class ValidationResult(BaseModel):
    command: list[str]
    description: str
    passed: bool
    returncode: int
    duration_seconds: float
    stdout: str = ""
    stderr: str = ""

class VerificationRunner:
    def run(self, repository: Path, validations: list[ValidationStep]) -> list[ValidationResult]:
        results = []
        for item in validations:
            start = time.monotonic()
            try:
                proc = subprocess.run(item.command, cwd=repository, capture_output=True, text=True, timeout=item.timeout_seconds, check=False)
                results.append(ValidationResult(command=item.command, description=item.description, passed=proc.returncode == 0, returncode=proc.returncode, duration_seconds=time.monotonic()-start, stdout=proc.stdout, stderr=proc.stderr))
            except subprocess.TimeoutExpired as exc:
                results.append(ValidationResult(command=item.command, description=item.description, passed=False, returncode=124, duration_seconds=time.monotonic()-start, stdout=exc.stdout or "", stderr=exc.stderr or "timeout"))
            if item.required and not results[-1].passed:
                break
        return results
