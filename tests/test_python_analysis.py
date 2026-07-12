from deconnected.python_analysis import analyze_python


def test_libcst_extracts_route_import_and_table():
    facts = analyze_python('''
from fastapi import APIRouter
from app.db import session
router = APIRouter()

class Order:
    __tablename__ = "orders"

@router.get("/api/orders/{order_id}")
def get_order(order_id: int):
    query = "SELECT * FROM orders WHERE id = 1"
    return session.execute(query)
''')
    assert "fastapi" in facts.imports
    assert ("GET", "/api/orders/{order_id}", 9) in facts.routes
    assert any(name == "orders" for name, _ in facts.table_names)
    assert facts.sql_literals
