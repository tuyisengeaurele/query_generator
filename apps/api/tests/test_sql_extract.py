from app.pipeline.sql_extract import extract_sql


def test_extracts_from_fenced_block_with_language_tag():
    raw = "Here is the query:\n```sql\nSELECT * FROM members\n```"
    assert extract_sql(raw) == "SELECT * FROM members"


def test_extracts_from_fenced_block_without_language_tag():
    raw = "```\nSELECT id FROM orders\n```"
    assert extract_sql(raw) == "SELECT id FROM orders"


def test_extracts_from_unfenced_response():
    raw = "SELECT name FROM products"
    assert extract_sql(raw) == "SELECT name FROM products"


def test_strips_trailing_semicolon():
    raw = "```sql\nSELECT 1;\n```"
    assert extract_sql(raw) == "SELECT 1"


def test_normalizes_multiline_sql_to_single_line():
    raw = "```sql\nSELECT id,\n  name\nFROM members\n```"
    assert extract_sql(raw) == "SELECT id, name FROM members"


def test_ignores_prose_before_and_after_fence():
    raw = "Sure, here you go:\n```sql\nSELECT 1\n```\nLet me know if you need more."
    assert extract_sql(raw) == "SELECT 1"


def test_strips_sql_comment_lines():
    raw = "```sql\n-- get all members\nSELECT * FROM members\n```"
    assert extract_sql(raw) == "SELECT * FROM members"
