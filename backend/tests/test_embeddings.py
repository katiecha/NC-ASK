import pytest


def test_sentence_transformer_embedding_generate_and_batch(monkeypatch):
    """Mock SentenceTransformer so tests run without downloading a model."""
    # Create a fake array-like object with tolist()
    class FakeArray:
        def __init__(self, vals):
            self._vals = vals

        def tolist(self):
            return list(self._vals)

    # Fake model with encode method
    class FakeModel:
        def __init__(self, name):
            self.name = name

        def encode(self, texts, convert_to_numpy=True):
            # Return single embedding for string input, or list for list input
            if isinstance(texts, str):
                return FakeArray([0.1, 0.2, 0.3])
            return FakeArray([[0.1, 0.2, 0.3] for _ in texts])

    # Monkeypatch the SentenceTransformer class in the module
    import services.embeddings as embeddings_module
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", FakeModel)

    emb = embeddings_module.SentenceTransformerEmbedding(model_name="dummy")

    single = emb.generate_embedding("hello world")
    assert isinstance(single, list)
    assert pytest.approx(single, rel=1e-3) == [0.1, 0.2, 0.3]

    batch = emb.generate_embeddings(["a", "b"])  # two texts
    assert isinstance(batch, list)
    assert len(batch) == 2
    assert batch[0] == [0.1, 0.2, 0.3]


def test_sentence_transformer_model_load_error(monkeypatch):
    """Ensure errors during model load are propagated."""
    def bad_init(name):
        raise RuntimeError("failed to load")

    import services.embeddings as embeddings_module
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", bad_init)

    emb = embeddings_module.SentenceTransformerEmbedding(model_name="broken")
    with pytest.raises(RuntimeError):
        # accessing .model should try to instantiate and raise
        _ = emb.model
