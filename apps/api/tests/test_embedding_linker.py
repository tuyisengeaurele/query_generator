from app.db.introspect import ColumnInfo, DatabaseSchema, ForeignKeyInfo, TableInfo
from app.pipeline.embedding_linker import EmbeddingSchemaLinker


def _wide_schema() -> DatabaseSchema:
    tables = []
    for name in ["members", "cooperatives", "products", "orders", "order_items", "payments", "warehouses", "shipments"]:
        tables.append(
            TableInfo(
                name=name,
                columns=[ColumnInfo(name="id", type="INTEGER", primary_key=True, nullable=False, sample_values=[])],
                foreign_keys=[],
            )
        )
    orders = next(t for t in tables if t.name == "orders")
    orders.foreign_keys = [ForeignKeyInfo(column="member_id", references_table="members", references_column="id")]
    return DatabaseSchema(tables=tables)


def test_embedding_linker_keeps_top_k_tables():
    linker = EmbeddingSchemaLinker(top_k=3)
    linked = linker.link("how many orders has each member placed", _wide_schema())
    assert len(linked.tables) >= 3


def test_embedding_linker_pulls_in_foreign_key_referenced_table():
    linker = EmbeddingSchemaLinker(top_k=1)
    linked = linker.link("how many orders has each member placed", _wide_schema())
    table_names = {t.name for t in linked.tables}
    if "orders" in table_names:
        assert "members" in table_names
