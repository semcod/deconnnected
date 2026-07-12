from __future__ import annotations

import re
from urllib.parse import urlparse

from deconnected.model import AppGraph, Edge


def _route_shape(value: str) -> str:
    path = urlparse(value).path if value.startswith(("http://", "https://")) else value
    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    path = re.sub(r"/[0-9a-fA-F-]{16,}(?=/|$)", "/{id}", path)
    return path.rstrip("/") or "/"


def correlate_runtime_to_routes(graph: AppGraph) -> int:
    """Link TestQL/browser URL nodes to statically detected route nodes."""
    route_nodes: dict[str, list[str]] = {}
    runtime_nodes: dict[str, list[str]] = {}
    for node_id, data in graph.graph.nodes(data=True):
        label = str(data.get("label") or "")
        if node_id.startswith("route:"):
            route_nodes.setdefault(_route_shape(label), []).append(node_id)
        elif node_id.startswith("url:") or node_id.startswith("testql:"):
            if label.startswith(("http://", "https://", "/")):
                runtime_nodes.setdefault(_route_shape(label), []).append(node_id)

    added = 0
    for shape, observed in runtime_nodes.items():
        for static_route in route_nodes.get(shape, []):
            for runtime_node in observed:
                graph.add_edge(Edge(
                    runtime_node, static_route, "observes_route",
                    f"normalized route match: {shape}", 0.92, True,
                ))
                added += 1
    return added
