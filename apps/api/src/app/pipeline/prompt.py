from app.pipeline.few_shot import ExamplePair
from app.pipeline.schema_linking import LinkedSchema

SYSTEM_INSTRUCTIONS = """You translate a natural language question into a single SQL SELECT statement.
Rules:
- Output exactly one SQL statement, and it must be a SELECT.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, or ATTACH.
- Use only the tables and columns given in the schema below.
- Return only the SQL, wrapped in a single ```sql fenced code block, no other prose."""


def build_prompt(question: str, schema: LinkedSchema, examples: list[ExamplePair]) -> str:
    parts = [SYSTEM_INSTRUCTIONS, "", "Schema:", "```sql", schema.render(), "```"]

    if examples:
        parts.append("")
        parts.append("Examples:")
        for example in examples:
            parts.append(f"Question: {example.question}")
            parts.append("```sql")
            parts.append(example.sql)
            parts.append("```")

    parts.append("")
    parts.append(f"Question: {question}")
    parts.append("SQL:")
    return "\n".join(parts)


def build_correction_prompt(question: str, schema: LinkedSchema, failed_sql: str, error: str) -> str:
    return "\n".join(
        [
            SYSTEM_INSTRUCTIONS,
            "",
            "Schema:",
            "```sql",
            schema.render(),
            "```",
            "",
            f"Question: {question}",
            "",
            "The previous attempt failed. Fix it.",
            "Previous SQL:",
            "```sql",
            failed_sql,
            "```",
            f"Database error: {error}",
            "",
            "SQL:",
        ]
    )
