from services.interfaces import RetrievalResult
from services.retrieval import DocumentRetrieval
from services.vector_store import InMemoryVectorStore


def make_result(idx, doc_id, title, text, score=0.5, url=None):
    return RetrievalResult(
        chunk_id=idx,
        chunk_text=text,
        document_id=doc_id,
        similarity_score=score,
        metadata={},
        document_title=title,
        source_url=url,
    )


def test_inmemory_store_and_search():
    store = InMemoryVectorStore()

    # embeddings in 2D space for simplicity
    chunks = [
        {"chunk_text": "A", "embedding": [1.0, 0.0], "document_id": 1, "chunk_index": 0},
        {"chunk_text": "B", "embedding": [0.0, 1.0], "document_id": 2, "chunk_index": 0},
    ]

    ids = store.store_document_chunks(chunks)
    assert ids == [1, 2]

    # Query similar to first chunk
    results = store.search_similar([1.0, 0.0], top_k=2, threshold=0.0)
    assert len(results) == 2
    # best match should be from document_id 1
    assert results[0].document_id == 1


def test_inmemory_threshold_and_clear():
    store = InMemoryVectorStore()
    store.store_document_chunks([{"chunk_text": "A", "embedding": [1.0, 0.0], "document_id": 1, "chunk_index": 0}])

    # High threshold should filter out
    results = store.search_similar([0.5, 0.5], top_k=1, threshold=0.99)
    assert results == []

    # clear and ensure no chunks
    store.clear()
    results = store.search_similar([1.0, 0.0], top_k=1, threshold=0.0)
    assert results == []


def test_document_retrieval_format_and_citations():
    # Create fake retrieval results
    results = [
        make_result(1, 1, "Doc One", "This is chunk one." , score=0.9, url="http://a"),
        make_result(2, 1, "Doc One", "This is chunk two.", score=0.8, url="http://a"),
        make_result(3, 2, "Doc Two", "Another chunk here.", score=0.7, url="http://b"),
    ]

    dr = DocumentRetrieval(vector_store=None, embedding_provider=None)

    context = dr.format_context_for_llm(results, max_tokens=1000)
    # Should include source attributions and chunk text
    assert "[Source 1: Doc One]" in context
    assert "This is chunk one." in context

    citations = dr.extract_citations(results)
    # Should return unique citations per document
    assert len(citations) == 2
    titles = {c["title"] for c in citations}
    assert "Doc One" in titles and "Doc Two" in titles


def test_document_retrieval_retrieve_calls_and_error_handling():
    # Mock embedding provider and vector store
    class FakeEmbedding:
        def generate_embedding(self, text):
            return [0.1, 0.2, 0.3]

    class FakeStore:
        def __init__(self):
            self.called_with = None

        def search_similar(self, query_embedding, top_k, threshold=0.1):
            self.called_with = (query_embedding, top_k, threshold)
            return [make_result(1, 1, "Doc", "chunk", score=0.5)]

    dr = DocumentRetrieval(vector_store=FakeStore(), embedding_provider=FakeEmbedding())

    res = dr.retrieve_similar_chunks("hello", top_k=1)
    assert isinstance(res, list)
    assert res[0].document_id == 1

    # Now simulate embedding provider raising
    class BadEmbedding:
        def generate_embedding(self, text):
            raise RuntimeError("embedding error")

    dr_bad = DocumentRetrieval(vector_store=FakeStore(), embedding_provider=BadEmbedding())
    res2 = dr_bad.retrieve_similar_chunks("x")
    assert res2 == []
