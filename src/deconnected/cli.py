from pathlib import Path
import json
import click
from rich.console import Console
from rich.table import Table
from deconnected.model import AppGraph
from deconnected.scanners.source import scan_source
from deconnected.scanners.config import scan_config
from deconnected.scanners.database import reflect_database
from deconnected.analysis import extraction_candidates
from deconnected.scanners.testql import import_testql_topology
from deconnected.frontend_tests import generate_frontend_checks, render_testql_scenario
from deconnected.correlation import correlate_runtime_to_routes
from deconnected.classification import classify_tables

console = Console()

@click.group()
def cli():
    """Map cross-layer dependencies and plan safe extractions."""

@cli.command()
@click.argument("root", type=click.Path(exists=True, path_type=Path))
@click.option("--database-url")
@click.option("--testql-topology", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path(".deconnected/graph.json"))
def scan(root: Path, database_url: str | None, testql_topology: Path | None, out: Path):
    graph = scan_source(root)
    graph.merge(scan_config(root))
    if database_url:
        graph.merge(reflect_database(database_url))
    if testql_topology:
        graph.merge(import_testql_topology(testql_topology))
        correlate_runtime_to_routes(graph)
    graph.to_json(out)
    console.print(f"Wrote {graph.graph.number_of_nodes()} nodes and {graph.graph.number_of_edges()} edges to {out}")

@cli.command("table-usage")
@click.argument("graph_file", type=click.Path(exists=True, path_type=Path))
def table_usage(graph_file: Path):
    graph = AppGraph.from_json(graph_file)
    table = Table("Table", "Reachable", "Refs", "Runtime", "Test-only")
    for row in graph.table_usage():
        table.add_row(row["table"], str(row["reachable_from_entrypoint"]), str(row["references"]), str(row["runtime_references"]), str(row["test_only_references"]))
    console.print(table)

@cli.command()
@click.argument("graph_file", type=click.Path(exists=True, path_type=Path))
def seams(graph_file: Path):
    console.print_json(json.dumps(extraction_candidates(AppGraph.from_json(graph_file))))

@cli.command()
@click.argument("graph_file", type=click.Path(exists=True, path_type=Path))
def report(graph_file: Path):
    graph = AppGraph.from_json(graph_file)
    payload = {"nodes": graph.graph.number_of_nodes(), "edges": graph.graph.number_of_edges(), "entrypoints": graph.entrypoints(), "tables": graph.table_usage(), "table_classifications": classify_tables(graph), "candidates": extraction_candidates(graph)}
    console.print_json(json.dumps(payload))


@cli.command("classify-tables")
@click.argument("graph_file", type=click.Path(exists=True, path_type=Path))
@click.option("--json-output", is_flag=True, help="Emit machine-readable JSON.")
def classify_table_usage(graph_file: Path, json_output: bool):
    """Classify tables using static reachability, runtime and test evidence."""
    rows = classify_tables(AppGraph.from_json(graph_file))
    if json_output:
        console.print_json(json.dumps(rows))
        return
    table = Table("Table", "Classification", "Confidence", "Removable", "Blockers")
    for row in rows:
        table.add_row(
            row["label"],
            row["classification"],
            f'{row["confidence"]:.2f}',
            str(row["removable"]),
            ", ".join(row["blockers"]) or "-",
        )
    console.print(table)


@cli.command("generate-frontend-tests")
@click.argument("topology_file", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path(".deconnected/generated-web.testql.toon.yaml"))
def generate_frontend_tests(topology_file: Path, out: Path):
    graph = import_testql_topology(topology_file)
    checks = generate_frontend_checks(graph)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_testql_scenario(checks), encoding="utf-8")
    console.print(f"Generated {len(checks)} frontend checks in {out}")

@cli.command("integrations")
def integrations_status():
    """Show optional ecosystem integrations and their availability."""
    from deconnected.integrations import available_integrations

    table = Table("Integration", "Available", "Purpose")
    for item in available_integrations():
        table.add_row(item["name"], str(item["available"]), item["purpose"])
    console.print(table)


@cli.command("ecosystem-scan")
@click.argument("root", type=click.Path(exists=True, path_type=Path))
@click.option("--target", help="Runtime URL passed to TestQL, e.g. http://localhost:8100")
@click.option(
    "--tools",
    default="testql,code2llm,code2logic,redup,regix,vallm,toonic",
    help="Comma-separated optional integrations.",
)
@click.option("--out", type=click.Path(path_type=Path), default=Path(".deconnected/ecosystem"))
@click.option("--timeout", type=int, default=900, show_default=True)
def ecosystem_scan(root: Path, target: str | None, tools: str, out: Path, timeout: int):
    """Run installed external analyzers and write one integration manifest."""
    from deconnected.integrations import run_pipeline

    names = [name.strip() for name in tools.split(",") if name.strip()]
    results = run_pipeline(names, root, out, target=target, timeout=timeout)
    table = Table("Integration", "Available", "Status", "Artifacts")
    for result in results:
        table.add_row(
            result.name,
            str(result.available),
            result.status,
            str(len(result.artifacts or [])),
        )
    console.print(table)
    console.print(f"Manifest: {out / 'manifest.json'}")

@cli.command("plan-refactor")
@click.argument("graph_file", type=click.Path(exists=True, path_type=Path))
@click.argument("objective")
@click.option("--out", type=click.Path(path_type=Path), default=Path(".deconnected/refactor-plan.json"))
@click.option("--provider", type=click.Choice(["none", "litellm", "claude-code"]), default="none")
@click.option("--model", default="openrouter/deepseek/deepseek-chat", show_default=True)
def plan_refactor(graph_file: Path, objective: str, out: Path, provider: str, model: str):
    """Create a constrained refactoring plan, optionally refined by an LLM."""
    from deconnected.agent.models import RefactorPlan
    from deconnected.agent.providers import LiteLLMProvider, ClaudeCodeProvider
    from deconnected.refactor.planner import build_rule_based_plan, build_llm_prompt

    graph = AppGraph.from_json(graph_file)
    plan = build_rule_based_plan(graph, objective)
    if provider != "none":
        summary = {"nodes": graph.graph.number_of_nodes(), "edges": graph.graph.number_of_edges(), "entrypoints": graph.entrypoints()}
        prompt = build_llm_prompt(plan, summary)
        engine = LiteLLMProvider(model=model) if provider == "litellm" else ClaudeCodeProvider()
        result = engine.create_plan(prompt, RefactorPlan.model_json_schema())
        if result.status != "success" or not result.structured:
            raise click.ClickException(result.error or "LLM planner failed")
        plan = RefactorPlan.model_validate(result.structured)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"Plan: {out}")
    console.print(f"Risk: {plan.risk}; confidence: {plan.confidence:.2f}; steps: {len(plan.steps)}")


@cli.command("simulate-refactor")
@click.argument("repository", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("plan_file", type=click.Path(exists=True, path_type=Path))
@click.option("--provider", type=click.Choice(["claude-code"]), default="claude-code")
@click.option("--keep-worktree", is_flag=True)
def simulate_refactor(repository: Path, plan_file: Path, provider: str, keep_worktree: bool):
    """Apply an approved plan inside an isolated git worktree."""
    from deconnected.agent.models import RefactorPlan
    from deconnected.agent.providers import ClaudeCodeProvider
    from deconnected.refactor.worktree import WorktreeManager
    from deconnected.refactor.verify import VerificationRunner

    plan = RefactorPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    if plan.blockers:
        raise click.ClickException("Plan has blockers: " + ", ".join(plan.blockers))
    manager = WorktreeManager(repository)
    worktree = manager.create(plan.id)
    run_dir = repository / ".deconnected" / "runs" / plan.id
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt = (
        "Apply only the approved plan. Do not modify files outside allowed_paths. "
        "Do not change public APIs or database schema. Stop on a blocker."
    )
    result = ClaudeCodeProvider().apply_plan(worktree, plan, prompt)
    (run_dir / "agent-result.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")
    if result.status != "success":
        console.print(f"Agent failed; worktree preserved at {worktree}")
        raise click.ClickException(result.error or "Agent execution failed")
    from deconnected.refactor.policy import evaluate_patch_policy
    from deconnected.refactor.snapshot import create_snapshot, diff_snapshots
    before = create_snapshot(repository, plan.allowed_paths)
    after = create_snapshot(worktree, plan.allowed_paths)
    (run_dir / "snapshot-before.json").write_text(before.model_dump_json(indent=2), encoding="utf-8")
    (run_dir / "snapshot-after.json").write_text(after.model_dump_json(indent=2), encoding="utf-8")
    (run_dir / "snapshot-diff.json").write_text(json.dumps(diff_snapshots(before, after), indent=2), encoding="utf-8")
    policy = evaluate_patch_policy(worktree, plan)
    (run_dir / "policy.json").write_text(policy.model_dump_json(indent=2), encoding="utf-8")
    validations = VerificationRunner().run(worktree, plan.validations) if policy.passed else []
    (run_dir / "verification.json").write_text(json.dumps([x.model_dump() for x in validations], indent=2), encoding="utf-8")
    diff = __import__('subprocess').run(["git", "diff", "--binary"], cwd=worktree, capture_output=True, text=True, check=False).stdout
    (run_dir / "patch.diff").write_text(diff, encoding="utf-8")
    passed = policy.passed and all(x.passed for x in validations)
    console.print(f"Worktree: {worktree}")
    console.print(f"Patch: {run_dir / 'patch.diff'}")
    console.print(f"Policy: {'passed' if policy.passed else 'blocked'}")
    console.print(f"Verification: {'passed' if passed else 'failed'}")
    if passed and not keep_worktree:
        manager.remove(worktree, force=True)


@cli.command("verify-refactor")
@click.argument("repository", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("plan_file", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path(".deconnected/verification.json"))
def verify_refactor(repository: Path, plan_file: Path, out: Path):
    """Run the validation matrix declared in a refactoring plan."""
    from deconnected.agent.models import RefactorPlan
    from deconnected.refactor.verify import VerificationRunner
    plan = RefactorPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    results = VerificationRunner().run(repository, plan.validations)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([x.model_dump() for x in results], indent=2), encoding="utf-8")
    failed = [x for x in results if not x.passed]
    console.print(f"Verification report: {out}")
    if failed:
        raise click.ClickException(f"{len(failed)} validation step(s) failed")
