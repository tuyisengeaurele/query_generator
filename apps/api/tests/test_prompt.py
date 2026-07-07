from app.pipeline.few_shot import ExamplePair
from app.pipeline.prompt import build_correction_prompt, build_prompt
from app.pipeline.schema_linking import LinkedColumn, LinkedSchema, LinkedTable


def _schema() -> LinkedSchema:
    return LinkedSchema(
        tables=[LinkedTable(name="members", columns=[LinkedColumn(name="id", type="INTEGER", sample_values=[])], foreign_keys=[])]
    )


def test_build_prompt_includes_question_schema_and_examples():
    examples = [ExamplePair(question="How many members?", sql="SELECT COUNT(*) FROM members")]
    prompt = build_prompt("How many members are there?", _schema(), examples)
    assert "How many members are there?" in prompt
    assert "TABLE members (" in prompt
    assert "SELECT COUNT(*) FROM members" in prompt
    assert "SELECT" in prompt


def test_build_prompt_omits_examples_section_when_none_given():
    prompt = build_prompt("How many members?", _schema(), [])
    assert "Examples:" not in prompt


def test_build_correction_prompt_includes_error_and_failed_sql():
    prompt = build_correction_prompt("How many members?", _schema(), "SELECT * FROM memebrs", "no such table: memebrs")
    assert "SELECT * FROM memebrs" in prompt
    assert "no such table: memebrs" in prompt
    assert "previous attempt failed" in prompt.lower()
