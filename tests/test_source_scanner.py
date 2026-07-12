from deconnected.scanners.source import scan_source

def test_links_gui_api_and_table(tmp_path):
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend" / "Orders.tsx").write_text('fetch("/api/orders")', encoding="utf-8")
    (tmp_path / "backend" / "routes.py").write_text('@router.get("/api/orders")\ndef x():\n return db.execute("SELECT * FROM orders")', encoding="utf-8")
    graph = scan_source(tmp_path)
    assert "table:orders" in graph.graph
    assert "route:/api/orders" in graph.graph
    assert any(data["kind"] == "uses_table" for _, _, data in graph.graph.edges(data=True))
