from __future__ import annotations
import re
from pathlib import Path
from deconnected.agent.models import RefactorPlan, RefactorStep, ValidationStep
from deconnected.model import AppGraph
from deconnected.analysis import extraction_candidates


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "refactor"


def build_rule_based_plan(graph: AppGraph, objective: str, root: Path | None = None) -> RefactorPlan:
    candidates = extraction_candidates(graph)
    top = candidates[0] if candidates else {"nodes": [], "cohesion": 0.0, "boundary_edges": 0}
    paths = sorted({graph.graph.nodes[n].get("path") for n in top.get("nodes", []) if n in graph.graph and graph.graph.nodes[n].get("path")})
    risk = "high" if top.get("boundary_edges", 0) > 5 else "medium"
    steps = [
        RefactorStep(id="checkpoint", operation="create_checkpoint", description="Create git checkpoint and isolated worktree", allowed_paths=[]),
        RefactorStep(id="introduce-seams", operation="introduce_interface", description="Introduce interfaces/adapters at cross-boundary edges", allowed_paths=paths, depends_on=["checkpoint"]),
        RefactorStep(id="extract", operation="extract_module", description="Move cohesive symbols into a smaller package while preserving compatibility imports", allowed_paths=paths, depends_on=["introduce-seams"]),
        RefactorStep(id="update-imports", operation="replace_direct_import", description="Update internal imports without changing public contracts", allowed_paths=paths, depends_on=["extract"]),
        RefactorStep(id="verify", operation="verify", description="Run tests and compare dependency graph before and after", allowed_paths=paths, depends_on=["update-imports"]),
    ]
    validations = [
        ValidationStep(command=["python", "-m", "compileall", "src"], description="Compile Python sources"),
        ValidationStep(command=["pytest", "-q"], description="Run test suite"),
        ValidationStep(command=["git", "diff", "--check"], description="Check patch whitespace and conflict markers"),
    ]
    return RefactorPlan(
        id=_safe_id(objective), objective=objective, risk=risk, affected_symbols=top.get("nodes", []), allowed_paths=paths,
        assumptions=["Public routes and response contracts remain unchanged", "Database objects are not dropped automatically"],
        steps=steps, validations=validations,
        blockers=[] if paths else ["No cohesive extraction candidate was found"],
        rollback=["Discard isolated worktree", "Reset branch to checkpoint"],
        confidence=min(0.95, max(0.25, float(top.get("cohesion", 0.0))))
    )


def build_llm_prompt(plan: RefactorPlan, graph_summary: dict) -> str:
    return (
        "You are a constrained refactoring planner. Use only supplied evidence. "
        "Do not delete database objects, change public API contracts, push remotes, or widen scope. "
        "Return a RefactorPlan JSON object.\n\n"
        f"Initial deterministic plan:\n{plan.model_dump_json(indent=2)}\n\n"
        f"Evidence graph summary:\n{graph_summary}\n"
    )
