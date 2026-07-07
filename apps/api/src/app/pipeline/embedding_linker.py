from __future__ import annotations

from app.db.introspect import DatabaseSchema, TableInfo
from app.pipeline.embeddings import Embedder, HashingEmbedder, cosine_similarity
from app.pipeline.schema_linking import LinkedSchema, SchemaLinker, _table_to_linked

DEFAULT_TOP_K_TABLES = 6


def _table_text(table: TableInfo) -> str:
    column_names = " ".join(c.name for c in table.columns)
    return f"{table.name} {column_names}"


class EmbeddingSchemaLinker(SchemaLinker):
    """Ranks tables by embedding similarity to the question and keeps the
    top-k, plus any table reachable by a foreign key from a selected table
    so joins stay possible. Used above EMBEDDING_LINKER_TABLE_THRESHOLD
    tables, where passing the full schema would blow the prompt budget."""

    def __init__(self, embedder: Embedder | None = None, top_k: int = DEFAULT_TOP_K_TABLES):
        self.embedder = embedder or HashingEmbedder()
        self.top_k = top_k

    def link(self, question: str, schema: DatabaseSchema) -> LinkedSchema:
        question_vector = self.embedder.embed(question)

        scored = [
            (cosine_similarity(question_vector, self.embedder.embed(_table_text(table))), table)
            for table in schema.tables
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        selected = {table.name: table for _, table in scored[: self.top_k]}

        for _, table in scored[: self.top_k]:
            for fk in table.foreign_keys:
                if fk.references_table not in selected:
                    referenced = next((t for t in schema.tables if t.name == fk.references_table), None)
                    if referenced is not None:
                        selected[referenced.name] = referenced

        ordered = [selected[table.name] for _, table in scored if table.name in selected]
        return LinkedSchema(tables=[_table_to_linked(t) for t in ordered])
