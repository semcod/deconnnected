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


def test_byte_string_assignment_does_not_crash():
    """evaluated_value is `bytes` for b"..."/rb"..." literals; regressions here
    crashed the whole scan with TypeError: cannot use a string pattern on a
    bytes-like object (visit_Assign -> _SQLISH.search)."""
    facts = analyze_python('''
MAGIC = b"SELECT * FROM users"
OTHER = rb"INSERT INTO orders"
''')
    assert facts.sql_literals == []

