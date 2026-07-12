import json
from deconnected.scanners.testql import import_testql_topology


def test_imports_testql_page_assets_and_edges(tmp_path):
    topology = {
        "confidence": "full",
        "nodes": [{
            "id": "page.root", "kind": "page", "source": "http://localhost:8100",
            "metadata": {"url": "http://localhost:8100", "assets": [
                {"url": "http://localhost:8100/main.js", "kind": "script"}
            ], "network_calls": []}, "evidence": []
        }],
        "edges": [],
    }
    path = tmp_path / "topology.json"
    path.write_text(json.dumps(topology), encoding="utf-8")
    graph = import_testql_topology(path)
    assert "testql:page.root" in graph.graph
    assert "url:http://localhost:8100/main.js" in graph.graph
    assert graph.graph.has_edge("testql:page.root", "url:http://localhost:8100/main.js")
