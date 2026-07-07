from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import Engine, inspect, text

SAMPLE_VALUES_PER_COLUMN = 3

_SCHEMA_CACHE: dict[str, "DatabaseSchema"] = {}


@dataclass
class ColumnInfo:
    name: str
    type: str
    primary_key: bool
    nullable: bool
    sample_values: list[str] = field(default_factory=list)


@dataclass
class ForeignKeyInfo:
    column: str
    references_table: str
    references_column: str


@dataclass
class TableInfo:
    name: str
    columns: list[ColumnInfo]
    foreign_keys: list[ForeignKeyInfo]


@dataclass
class DatabaseSchema:
    tables: list[TableInfo]

    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]


def _sample_values(engine: Engine, table_name: str, column_name: str) -> list[str]:
    try:
        with engine.connect() as conn:
            quoted_table = f'"{table_name}"'
            quoted_column = f'"{column_name}"'
            query = text(
                f"SELECT DISTINCT {quoted_column} FROM {quoted_table} "
                f"WHERE {quoted_column} IS NOT NULL LIMIT {SAMPLE_VALUES_PER_COLUMN}"
            )
            rows = conn.execute(query).fetchall()
            return [str(row[0]) for row in rows]
    except Exception:
        return []


def introspect_schema(engine: Engine, *, use_cache: bool = True, include_samples: bool = True) -> DatabaseSchema:
    cache_key = str(engine.url)
    if use_cache and cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]

    inspector = inspect(engine)
    tables: list[TableInfo] = []

    for table_name in inspector.get_table_names():
        pk_columns = set(inspector.get_pk_constraint(table_name).get("constrained_columns") or [])

        columns = []
        for col in inspector.get_columns(table_name):
            samples = (
                _sample_values(engine, table_name, col["name"]) if include_samples else []
            )
            columns.append(
                ColumnInfo(
                    name=col["name"],
                    type=str(col["type"]),
                    primary_key=col["name"] in pk_columns,
                    nullable=col.get("nullable", True),
                    sample_values=samples,
                )
            )

        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            referred_table = fk.get("referred_table")
            constrained = fk.get("constrained_columns") or []
            referred = fk.get("referred_columns") or []
            for local_col, remote_col in zip(constrained, referred):
                foreign_keys.append(
                    ForeignKeyInfo(
                        column=local_col,
                        references_table=referred_table,
                        references_column=remote_col,
                    )
                )

        tables.append(TableInfo(name=table_name, columns=columns, foreign_keys=foreign_keys))

    schema = DatabaseSchema(tables=tables)
    if use_cache:
        _SCHEMA_CACHE[cache_key] = schema
    return schema


def clear_schema_cache() -> None:
    _SCHEMA_CACHE.clear()
