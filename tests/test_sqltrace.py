from sqlalchemy import create_engine, text
from deconnected.runtime.sqltrace import SqlTrace

def test_runtime_sql_trace_detects_table():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("create table orders(id integer primary key)"))
    with SqlTrace(engine) as trace:
        with engine.begin() as connection:
            connection.execute(text("select * from orders"))
    assert "orders" in trace.tables
