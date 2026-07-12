from __future__ import annotations

from dataclasses import dataclass, asdict
from deconnected.model import AppGraph


@dataclass(frozen=True)
class UsageClassification:
    node_id: str
    label: str
    classification: str
    confidence: float
    removable: bool
    blockers: tuple[str, ...]
    evidence_count: int

    def to_dict(self) -> dict:
        result = asdict(self)
        result["blockers"] = list(self.blockers)
        return result


def classify_tables(app: AppGraph) -> list[dict]:
    reachable = app.reachable()
    results: list[UsageClassification] = []
    for node_id, data in app.graph.nodes(data=True):
        if data.get("kind") != "table":
            continue
        incoming = list(app.graph.in_edges(node_id, data=True))
        runtime = sum(bool(edge.get("runtime")) for _, _, edge in incoming)
        tests = sum(bool(edge.get("test_only")) for _, _, edge in incoming)
        non_test = len(incoming) - tests
        blockers: list[str] = []

        if runtime:
            status, confidence = "actively_used", 0.98
            blockers.append("runtime_observation")
        elif node_id in reachable and non_test:
            status, confidence = "statically_reachable", 0.86
            blockers.append("reachable_from_entrypoint")
        elif incoming and tests == len(incoming):
            status, confidence = "test_only", 0.82
            blockers.append("test_reference")
        elif incoming:
            status, confidence = "statically_referenced", 0.72
            blockers.append("static_reference")
        else:
            status, confidence = "probable_legacy", 0.76

        removable = not blockers and status == "probable_legacy"
        results.append(UsageClassification(
            node_id=node_id,
            label=data.get("label", node_id),
            classification=status,
            confidence=confidence,
            removable=removable,
            blockers=tuple(blockers),
            evidence_count=len(incoming),
        ))
    return [item.to_dict() for item in sorted(results, key=lambda item: item.label)]
