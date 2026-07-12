from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

Risk = Literal["low", "medium", "high", "critical"]

class RefactorStep(BaseModel):
    id: str
    operation: str
    description: str
    allowed_paths: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    requires_approval: bool = False

class ValidationStep(BaseModel):
    command: list[str]
    description: str
    required: bool = True
    timeout_seconds: int = 900

class RefactorPlan(BaseModel):
    id: str
    objective: str
    risk: Risk = "medium"
    assumptions: list[str] = Field(default_factory=list)
    affected_symbols: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    forbidden_operations: list[str] = Field(default_factory=lambda: [
        "drop_database_table", "rewrite_public_api", "push_remote", "delete_git_history"
    ])
    steps: list[RefactorStep]
    validations: list[ValidationStep] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    rollback: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AgentRunResult(BaseModel):
    provider: str
    status: Literal["success", "failed", "blocked"]
    output: str = ""
    structured: dict | None = None
    returncode: int = 0
    artifacts: list[str] = Field(default_factory=list)
    error: str | None = None

class PatchContext(BaseModel):
    repository: str
    plan_file: str
    worktree: str | None = None
    prompt_file: str | None = None
