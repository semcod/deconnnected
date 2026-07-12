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


def test_ignores_secondary_venvs_and_vendored_packages(tmp_path):
    """The exact-match IGNORE set misses ".venv-test" (a second venv
    alongside ".venv") and site-packages/*.egg-info dirs inside any venv —
    left unfiltered, a scan spends nearly all its time walking vendored
    third-party code instead of the application's own source. Found
    scanning maskservice/c2004, which has connect-scenario/backend/.venv-test
    bundling litellm/openai/anthropic/pip's vendored deps."""
    noisy = tmp_path / "backend" / ".venv-test" / "lib" / "site-packages" / "somepkg.egg-info"
    noisy.mkdir(parents=True)
    (noisy / "vendored.py").write_text('db.execute("SELECT * FROM vendored_table")', encoding="utf-8")
    (tmp_path / "backend").joinpath("app.py").write_text('db.execute("SELECT * FROM real_table")', encoding="utf-8")

    graph = scan_source(tmp_path)
    assert "table:real_table" in graph.graph
    assert "table:vendored_table" not in graph.graph
