from app.pipeline.few_shot import ExamplePair, FewShotRetriever, load_examples


def test_load_examples_reads_bundled_pairs_file():
    examples = load_examples()
    assert len(examples) >= 5
    assert all(e.sql.strip().upper().startswith("SELECT") for e in examples)


def test_retriever_ranks_by_keyword_overlap():
    examples = [
        ExamplePair(question="How many members does each cooperative have?", sql="SELECT 1"),
        ExamplePair(question="What is the average order value per member?", sql="SELECT 2"),
        ExamplePair(question="List products never ordered", sql="SELECT 3"),
    ]
    retriever = FewShotRetriever(examples)
    results = retriever.retrieve("how many members are in each cooperative", top_k=1)
    assert results[0].sql == "SELECT 1"


def test_retriever_respects_top_k():
    examples = [ExamplePair(question=f"question {i}", sql=f"SELECT {i}") for i in range(10)]
    retriever = FewShotRetriever(examples)
    results = retriever.retrieve("question 3", top_k=2)
    assert len(results) == 2
