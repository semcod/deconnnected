from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
from typing import Iterable


@dataclass(frozen=True)
class IntegrationSpec:
    name: str
    module: str
    executable: str
    purpose: str
    args: tuple[str, ...]


@dataclass
class IntegrationResult:
    name: str
    available: bool
    status: str
    command: list[str]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    artifacts: list[str] | None = None

    def to_dict(self) -> dict:
        return asdict(self)


SPECS: dict[str, IntegrationSpec] = {
    "testql": IntegrationSpec(
        "testql", "testql", "testql",
        "Browser/API discovery, runtime topology and generated web tests.",
        ("inspect", "{target}", "--out-dir", "{out}/testql"),
    ),
    "code2llm": IntegrationSpec(
        "code2llm", "code2llm", "code2llm",
        "CFG, DFG, call graphs, coupling and TOON architecture outputs.",
        ("{root}", "-f", "all", "-o", "{out}/code2llm"),
    ),
    "code2logic": IntegrationSpec(
        "code2logic", "code2logic", "code2logic",
        "Semantic code-flow and project logic analysis.",
        ("{root}", "--output", "{out}/code2logic"),
    ),
    "redup": IntegrationSpec(
        "redup", "redup", "redup",
        "Exact, structural and fuzzy duplication plus extraction suggestions.",
        ("scan", "{root}", "--fuzzy", "--output", "{out}/redup.json", "--format", "json"),
    ),
    "regix": IntegrationSpec(
        "regix", "regix", "regix",
        "Git-native regression and architecture delta detection.",
        ("scan", "{root}", "--output", "{out}/regix.json"),
    ),
    "vallm": IntegrationSpec(
        "vallm", "vallm", "vallm",
        "Syntax, import, security and semantic validation of refactoring changes.",
        ("validate", "{root}", "--output", "{out}/vallm.json"),
    ),
    "toonic": IntegrationSpec(
        "toonic", "toonic", "toonic",
        "Conversion and normalization of reports into TOON representations.",
        ("convert", "{out}/manifest.json", "--output", "{out}/manifest.toon.yaml"),
    ),
}


def _available(spec: IntegrationSpec) -> bool:
    return bool(shutil.which(spec.executable) or importlib.util.find_spec(spec.module))


def available_integrations() -> list[dict]:
    return [
        {"name": spec.name, "available": _available(spec), "purpose": spec.purpose}
        for spec in SPECS.values()
    ]


def _render_args(spec: IntegrationSpec, root: Path, out: Path, target: str | None) -> list[str]:
    values = {"root": str(root), "out": str(out), "target": target or str(root)}
    return [arg.format(**values) for arg in spec.args]


def run_integration(
    name: str,
    root: Path,
    out: Path,
    *,
    target: str | None = None,
    timeout: int = 900,
) -> IntegrationResult:
    if name not in SPECS:
        raise ValueError(f"Unknown integration: {name}")
    spec = SPECS[name]
    args = _render_args(spec, root.resolve(), out.resolve(), target)
    command = [spec.executable, *args]
    if not _available(spec):
        return IntegrationResult(name, False, "missing", command, artifacts=[])

    out.mkdir(parents=True, exist_ok=True)
    before = {str(p) for p in out.rglob("*") if p.is_file()}
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return IntegrationResult(name, True, "error", command, stderr=str(exc), artifacts=[])

    after = {str(p) for p in out.rglob("*") if p.is_file()}
    return IntegrationResult(
        name=name,
        available=True,
        status="passed" if completed.returncode == 0 else "failed",
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout[-12000:],
        stderr=completed.stderr[-12000:],
        artifacts=sorted(after - before),
    )


def run_pipeline(
    names: Iterable[str],
    root: Path,
    out: Path,
    *,
    target: str | None = None,
    timeout: int = 900,
) -> list[IntegrationResult]:
    out.mkdir(parents=True, exist_ok=True)
    results = [run_integration(n, root, out, target=target, timeout=timeout) for n in names]
    manifest = {
        "tool": "deconnected",
        "root": str(root.resolve()),
        "results": [r.to_dict() for r in results],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return results
