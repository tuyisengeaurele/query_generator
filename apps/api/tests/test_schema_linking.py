from app.db.introspect import ColumnInfo, DatabaseSchema, ForeignKeyInfo, TableInfo
from app.pipeline.schema_linking import FullSchemaLinker


def _sample_schema() -> DatabaseSchema:
    members = TableInfo(
        name="members",
        columns=[
            ColumnInfo(name="id", type="INTEGER", primary_key=True, nullable=False, sample_values=["1", "2"]),
            ColumnInfo(name="full_name", type="TEXT", primary_key=False, nullable=False, sample_values=["Alice"]),
            ColumnInfo(name="cooperative_id", type="INTEGER", primary_key=False, nullable=True, sample_values=[]),
        ],
        foreign_keys=[ForeignKeyInfo(column="cooperative_id", references_table="cooperatives", references_column="id")],
    )
    cooperatives = TableInfo(
        name="cooperatives",
        columns=[
            ColumnInfo(name="id", type="INTEGER", primary_key=True, nullable=False, sample_values=["1"]),
            ColumnInfo(name="name", type="TEXT", primary_key=False, nullable=False, sample_values=["Kigali Growers"]),
        ],
        foreign_keys=[],
    )
    return DatabaseSchema(tables=[members, cooperatives])


def test_full_schema_linker_includes_every_table():
    linker = FullSchemaLinker()
    linked = linker.link("how many members are there", _sample_schema())
    table_names = [t.name for t in linked.tables]
    assert table_names == ["members", "cooperatives"]


def test_full_schema_linker_preserves_foreign_keys():
    linker = FullSchemaLinker()
    linked = linker.link("any question", _sample_schema())
    members = next(t for t in linked.tables if t.name == "members")
    assert any("cooperatives" in fk for fk in members.foreign_keys)


def test_render_produces_ddl_like_text_with_samples():
    linker = FullSchemaLinker()
    linked = linker.link("any question", _sample_schema())
    rendered = linked.render()
    assert "TABLE members (" in rendered
    assert "full_name TEXT" in rendered
    assert "e.g. Alice" in rendered
