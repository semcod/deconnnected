from sqlalchemy import create_engine, inspect
from deconnected.model import AppGraph, Node, Edge

def reflect_database(url: str) -> AppGraph:
    graph = AppGraph()
    inspector = inspect(create_engine(url))
    for schema in inspector.get_schema_names():
        if schema in {"information_schema", "pg_catalog"}:
            continue
        for table in inspector.get_table_names(schema=schema):
            table_id = f"table:{table}"
            graph.add_node(Node(table_id, "table", table, metadata={"schema": schema}))
            for fk in inspector.get_foreign_keys(table, schema=schema):
                target = fk.get("referred_table")
                if target:
                    target_id = f"table:{target}"
                    graph.add_node(Node(target_id, "table", target))
                    graph.add_edge(Edge(table_id, target_id, "foreign_key", f"{schema}.{table}", 1.0))
    return graph
