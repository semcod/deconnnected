from __future__ import annotations
from pathlib import Path
import yaml
from deconnected.model import AppGraph, Node, Edge

def scan_config(root: Path) -> AppGraph:
    graph = AppGraph()
    files = list(root.glob("docker-compose*.yml")) + list(root.glob("docker-compose*.yaml"))
    for path in files:
        rel = path.relative_to(root).as_posix()
        config_id = f"config:{rel}"
        graph.add_node(Node(config_id, "config", rel, rel))
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        for name, spec in (data.get("services") or {}).items():
            service_id = f"service:{name}"
            graph.add_node(Node(service_id, "service", name, rel))
            graph.add_edge(Edge(config_id, service_id, "defines_service", rel, 0.98))
            dependencies = (spec or {}).get("depends_on", []) or []
            if isinstance(dependencies, dict):
                dependencies = dependencies.keys()
            for dependency in dependencies:
                target_id = f"service:{dependency}"
                graph.add_node(Node(target_id, "service", str(dependency), rel))
                graph.add_edge(Edge(service_id, target_id, "depends_on", rel, 0.98))
    return graph
