from __future__ import annotations

import networkx as nx
from deconnected.model import AppGraph


def extraction_candidates(app: AppGraph, min_size: int = 2) -> list[dict]:
    simple = nx.DiGraph()
    simple.add_nodes_from(app.graph.nodes(data=True))
    simple.add_edges_from((u, v) for u, v in app.graph.edges())
    candidates = []
    for component in nx.connected_components(simple.to_undirected()):
        if len(component) < min_size:
            continue
        internal = simple.subgraph(component).number_of_edges()
        boundary = sum(1 for u, v in simple.edges() if (u in component) != (v in component))
        cohesion = internal / max(1, internal + boundary)
        candidates.append({
            "nodes": sorted(component),
            "size": len(component),
            "internal_edges": internal,
            "boundary_edges": boundary,
            "cohesion": round(cohesion, 3),
            "recommendation": "extract_candidate" if cohesion >= 0.7 else "needs_seams",
        })
    return sorted(candidates, key=lambda item: (item["cohesion"], item["size"]), reverse=True)
