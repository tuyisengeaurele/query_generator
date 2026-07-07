from app.pipeline.embeddings import HashingEmbedder, cosine_similarity


def test_hashing_embedder_is_deterministic():
    embedder = HashingEmbedder()
    a = embedder.embed("how many members are in the cooperative")
    b = embedder.embed("how many members are in the cooperative")
    assert (a == b).all()


def test_hashing_embedder_similar_text_scores_higher_than_unrelated():
    embedder = HashingEmbedder()
    question = embedder.embed("how many members does the cooperative have")
    close = embedder.embed("members cooperative count")
    far = embedder.embed("total revenue by product category")

    assert cosine_similarity(question, close) > cosine_similarity(question, far)


def test_cosine_similarity_of_identical_vectors_is_one():
    embedder = HashingEmbedder()
    vector = embedder.embed("payments and orders")
    assert cosine_similarity(vector, vector) > 0.999
