from deconnected.scanners.config import scan_config

def test_compose_dependencies(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("services:\n  api:\n    depends_on:\n      - db\n  db:\n    image: postgres:16\n", encoding="utf-8")
    graph = scan_config(tmp_path)
    assert graph.graph.has_edge("service:api", "service:db")
