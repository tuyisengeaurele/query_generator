from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.db.introspect import ColumnInfo, DatabaseSchema, TableInfo


@dataclass
class LinkedColumn:
    name: str
    type: str
    sample_values: list[str]


@dataclass
class LinkedTable:
    name: str
    columns: list[LinkedColumn]
    foreign_keys: list[str]


@dataclass
class LinkedSchema:
    tables: list[LinkedTable]

    def render(self) -> str:
        """Render as compact DDL-like text for the prompt. Always monospace
        in the UI, and this is the exact text the model sees."""
        lines = []
        for table in self.tables:
            lines.append(f"TABLE {table.name} (")
            for column in table.columns:
                sample_note = f"  -- e.g. {', '.join(column.sample_values)}" if column.sample_values else ""
                lines.append(f"  {column.name} {column.type}{sample_note}")
            for fk in table.foreign_keys:
                lines.append(f"  {fk}")
            lines.append(")")
        return "\n".join(lines)


def _table_to_linked(table: TableInfo, column_filter: set[str] | None = None) -> LinkedTable:
    columns: list[ColumnInfo] = table.columns
    if column_filter is not None:
        columns = [c for c in columns if c.name in column_filter]

    fk_lines = [
        f"FOREIGN KEY ({fk.column}) REFERENCES {fk.references_table}({fk.references_column})"
        for fk in table.foreign_keys
    ]

    return LinkedTable(
        name=table.name,
        columns=[LinkedColumn(name=c.name, type=c.type, sample_values=c.sample_values) for c in columns],
        foreign_keys=fk_lines,
    )


class SchemaLinker(ABC):
    """Selects which tables and columns are relevant to a question. The
    strategy is swappable: full-schema pass-through for small schemas,
    embedding-based ranking for large ones."""

    @abstractmethod
    def link(self, question: str, schema: DatabaseSchema) -> LinkedSchema:
        raise NotImplementedError


class FullSchemaLinker(SchemaLinker):
    """Passes the entire schema through unfiltered. Correct default when the
    schema is small enough to fit the prompt budget."""

    def link(self, question: str, schema: DatabaseSchema) -> LinkedSchema:
        return LinkedSchema(tables=[_table_to_linked(t) for t in schema.tables])
