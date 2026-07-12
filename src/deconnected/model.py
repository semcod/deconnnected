from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import networkx as nx

@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    label: str
    path: str | None = None
    metadata: dict | None = None

@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    kind: str
    evidence: str
    confidence: float = 0.5
    runtime: bool = False
    test_only: bool = False

class AppGraph:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: Node) -> None:
        self.graph.add_node(node.id, **asdict(node))

    def add_edge(self, edge: Edge) -> None:
        self.graph.add_edge(edge.source, edge.target, **asdict(edge))

    def merge(self, other: "AppGraph") -> None:
        self.graph = nx.compose(self.graph, other.graph)

    def entrypoints(self) -> list[str]:
        kinds = {"gui", "api", "job", "cli", "service"}
        return [n for n, d in self.graph.nodes(data=True) if d.get("kind") in kinds]

    def reachable(self) -> set[str]:
        found: set[str] = set()
        for source in self.entrypoints():
            found.add(source)
            found.update(nx.descendants(self.graph, source))
        return found

    def table_usage(self) -> list[dict]:
        reachable = self.reachable()
        rows = []
        for node, data in self.graph.nodes(data=True):
            if data.get("kind") != "table":
                continue
            incoming = list(self.graph.in_edges(node, data=True))
            rows.append({
                "table": data.get("label"),
                "reachable_from_entrypoint": node in reachable,
                "references": len(incoming),
                "runtime_references": sum(bool(e.get("runtime")) for _, _, e in incoming),
                "test_only_references": sum(bool(e.get("test_only")) for _, _, e in incoming),
                "evidence": [e.get("evidence") for _, _, e in incoming],
            })
        return sorted(rows, key=lambda row: row["table"])

    def to_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = nx.node_link_data(self.graph, edges="edges")
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Path) -> "AppGraph":
        obj = cls()
        payload = json.loads(path.read_text(encoding="utf-8"))
        obj.graph = nx.node_link_graph(payload, edges="edges", directed=True, multigraph=True)
        return obj
