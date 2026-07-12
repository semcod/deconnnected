from deconnected.sql_analysis import extract_sql_references


def test_sqlglot_extracts_read_and_write_tables():
    refs = extract_sql_references(
        "SELECT o.id FROM orders o JOIN users u ON u.id=o.user_id; "
        "UPDATE invoices SET paid = true WHERE id = 1"
    )
    values = {(ref.table, ref.operation) for ref in refs}
    assert ("orders", "select") in values
    assert ("users", "select") in values
    assert ("invoices", "update") in values
