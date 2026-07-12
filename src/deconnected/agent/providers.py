from __future__ import annotations
import json
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from .models import AgentRunResult, RefactorPlan
from .budget import BudgetPolicy

class ReasoningProvider(ABC):
    @abstractmethod
    def create_plan(self, prompt: str, schema: dict[str, Any]) -> AgentRunResult: ...

    def apply_plan(self, repository: Path, plan: RefactorPlan, prompt: str) -> AgentRunResult:
        return AgentRunResult(provider=self.__class__.__name__, status="blocked", error="Provider cannot edit repositories")

class LiteLLMProvider(ReasoningProvider):
    def __init__(self, model: str, api_base: str | None = None, api_key: str | None = None, budget: BudgetPolicy | None = None):
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.budget = budget or BudgetPolicy()
        self.budget.validate()

    def create_plan(self, prompt: str, schema: dict[str, Any]) -> AgentRunResult:
        try:
            from litellm import completion
        except ImportError as exc:
            return AgentRunResult(provider="litellm", status="failed", error=f"Install deconnected[llm]: {exc}")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": self.budget.max_output_tokens,
            "response_format": {"type": "json_schema", "json_schema": {"name": "refactor_plan", "schema": schema}},
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key
        try:
            response = completion(**kwargs)
            content = response.choices[0].message.content
            payload = json.loads(content)
            return AgentRunResult(provider="litellm", status="success", output=content, structured=payload)
        except Exception as exc:  # provider-specific errors vary
            return AgentRunResult(provider="litellm", status="failed", error=str(exc))

class ClaudeCodeProvider(ReasoningProvider):
    def __init__(self, executable: str = "claude", timeout: int = 1800, allowed_tools: str | None = None):
        self.executable = executable
        self.timeout = timeout
        self.allowed_tools = allowed_tools or "Read,Glob,Grep,Edit,Bash(pytest:*),Bash(npm test:*),Bash(git diff:*),Bash(ruff:*)"

    def _run(self, repository: Path, prompt: str) -> AgentRunResult:
        command = [self.executable, "-p", prompt, "--output-format", "json", "--allowedTools", self.allowed_tools]
        try:
            result = subprocess.run(command, cwd=repository, capture_output=True, text=True, timeout=self.timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return AgentRunResult(provider="claude-code", status="failed", error=str(exc), returncode=127)
        status = "success" if result.returncode == 0 else "failed"
        structured = None
        try:
            structured = json.loads(result.stdout) if result.stdout.strip() else None
        except json.JSONDecodeError:
            pass
        return AgentRunResult(provider="claude-code", status=status, output=result.stdout, structured=structured, returncode=result.returncode, error=result.stderr or None)

    def create_plan(self, prompt: str, schema: dict[str, Any]) -> AgentRunResult:
        augmented = prompt + "\nReturn only JSON matching this schema:\n" + json.dumps(schema)
        return self._run(Path.cwd(), augmented)

    def apply_plan(self, repository: Path, plan: RefactorPlan, prompt: str) -> AgentRunResult:
        return self._run(repository, prompt + "\nApproved plan:\n" + plan.model_dump_json(indent=2))
