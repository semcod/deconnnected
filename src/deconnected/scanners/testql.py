from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from deconnected.model import AppGraph, Edge, Node

_KIND_MAP = {
    "page": "gui",
    "interface": "gui",
    "http_endpoint": "api",
    "asset": "asset",
    "form": "form",
    "sitemap": "sitemap",
    "artifact": "artifact",
    "artifact_type": "artifact_type",
    "evidence": "evidence",
}


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text) or {}


def import_testql_topology(path: Path) -> AppGraph:
    """Import TestQL topology JSON/YAML/TOON-YAML into Deconnected's graph."""
    payload = _load(path)
    graph = AppGraph()

    for raw in payload.get("nodes", []):
        node_id = f"testql:{raw['id']}"
        raw_kind = str(raw.get("kind", "artifact"))
        metadata = dict(raw.get("metadata") or {})
        source = raw.get("source")
        if isinstance(source, dict):
            source_value = source.get("location") or json.dumps(source, sort_keys=True)
        else:
            source_value = source
        label = (
            metadata.get("url")
            or metadata.get("location")
            or metadata.get("type")
            or source_value
            or raw["id"]
        )
        graph.add_node(Node(
            id=node_id,
            kind=_KIND_MAP.get(raw_kind, raw_kind),
            label=str(label),
            path=None,
            metadata={
                **metadata,
                "testql_kind": raw_kind,
                "testql_source": source,
                "testql_evidence": raw.get("evidence", []),
            },
        ))

    for raw in payload.get("edges", []):
        source = f"testql:{raw['source_id']}"
        target = f"testql:{raw['target_id']}"
        evidence_items = raw.get("evidence") or []
        evidence = "; ".join(
            str(item.get("detail") or item.get("location") or item)
            for item in evidence_items
        ) or f"testql:{path.name}"
        graph.add_edge(Edge(
            source=source,
            target=target,
            kind=str(raw.get("relation", "related_to")),
            evidence=evidence,
            confidence=1.0 if payload.get("confidence") == "full" else 0.75,
            runtime=str(raw.get("protocol")) in {"browser", "http", "websocket"},
        ))

    # Materialize assets/network calls as canonical URL nodes so they can be
    # matched with source-code literals and runtime traces from other scanners.
    for node_id, data in list(graph.graph.nodes(data=True)):
        metadata = data.get("metadata") or {}
        for asset in metadata.get("assets", []) or []:
            url = asset.get("url")
            if not url:
                continue
            canonical = f"url:{url}"
            graph.add_node(Node(canonical, "asset", url, metadata=asset))
            graph.add_edge(Edge(node_id, canonical, "loads", f"testql:{path.name}", 1.0, True))
        for call in metadata.get("network_calls", []) or []:
            url = call.get("url") if isinstance(call, dict) else str(call)
            if not url:
                continue
            canonical = f"url:{url}"
            graph.add_node(Node(canonical, "api", url, metadata=call if isinstance(call, dict) else {}))
            graph.add_edge(Edge(node_id, canonical, "calls_api", f"testql:{path.name}", 1.0, True))

    return graph
