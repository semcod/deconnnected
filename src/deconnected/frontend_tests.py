from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from deconnected.model import AppGraph


@dataclass(frozen=True)
class GeneratedCheck:
    id: str
    kind: str
    target: str
    assertion: str
    source_node: str


def generate_frontend_checks(graph: AppGraph) -> list[GeneratedCheck]:
    """Generate deterministic black-box checks from imported web topology."""
    checks: list[GeneratedCheck] = []
    seen: set[tuple[str, str]] = set()

    for node_id, data in graph.graph.nodes(data=True):
        kind = data.get("kind")
        label = str(data.get("label") or "")
        metadata = data.get("metadata") or {}

        if kind == "gui" and label.startswith(("http://", "https://")):
            key = ("page_status", label)
            if key not in seen:
                checks.append(GeneratedCheck(
                    f"page-{len(checks)+1}", "page_status", label,
                    "status < 400 and document renders", node_id,
                ))
                seen.add(key)

        if kind == "asset" and label.startswith(("http://", "https://")):
            key = ("asset_status", label)
            if key not in seen:
                checks.append(GeneratedCheck(
                    f"asset-{len(checks)+1}", "asset_status", label,
                    "status < 400", node_id,
                ))
                seen.add(key)

        for form in metadata.get("forms", []) or []:
            action = form.get("action") or label
            key = ("form", action)
            if key not in seen:
                checks.append(GeneratedCheck(
                    f"form-{len(checks)+1}", "form", action,
                    "form is visible and submit target is reachable", node_id,
                ))
                seen.add(key)

    return checks


def render_testql_scenario(checks: list[GeneratedCheck], title: str = "Deconnected generated frontend checks") -> str:
    """Render a conservative TestTOON scenario using HTTP-safe checks."""
    urls = [c.target for c in checks if c.kind in {"page_status", "asset_status"}]
    lines = [
        f"# SCENARIO: {title}",
        "# TYPE: generated-web-smoke",
        "# VERSION: 1.0",
        "",
        f"API[{len(urls)}]{{method, endpoint, status}}:",
    ]
    for url in urls:
        parsed = urlparse(url)
        endpoint = parsed.path or "/"
        if parsed.query:
            endpoint += "?" + parsed.query
        lines.append(f"  GET, {endpoint}, 200")
    if not urls:
        lines.append("  # no HTTP checks discovered")
    return "\n".join(lines) + "\n"
