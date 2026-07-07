from app.db.introspect import clear_schema_cache, introspect_schema


def test_introspect_lists_tables_and_columns(sqlite_engine):
    clear_schema_cache()
    schema = introspect_schema(sqlite_engine, use_cache=False)

    table_names = schema.table_names()
    assert "members" in table_names
    assert "cooperatives" in table_names

    members = next(t for t in schema.tables if t.name == "members")
    column_names = [c.name for c in members.columns]
    assert column_names == ["id", "full_name", "cooperative_id"]

    id_column = next(c for c in members.columns if c.name == "id")
    assert id_column.primary_key is True


def test_introspect_captures_sample_values(sqlite_engine):
    schema = introspect_schema(sqlite_engine, use_cache=False, include_samples=True)
    cooperatives = next(t for t in schema.tables if t.name == "cooperatives")
    name_column = next(c for c in cooperatives.columns if c.name == "name")
    assert "Kigali Growers" in name_column.sample_values


def test_introspect_uses_cache_by_default(sqlite_engine):
    clear_schema_cache()
    first = introspect_schema(sqlite_engine)
    second = introspect_schema(sqlite_engine)
    assert first is second
