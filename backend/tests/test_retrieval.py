import pytest
from services.service_factory import ServiceFactory


def test_retrieval_service():
    """Test retrieval service returns results with seeded test data."""
    # Use in-memory vector store to avoid real Supabase connection
    factory = ServiceFactory(use_in_memory_store=True)

    # Seed the in-memory vector store with test data
    vector_store = factory.get_vector_store()
    embedding_provider = factory.get_embedding_provider()

    # Create test chunks about autism
    test_documents = [
        {
            "chunk_text": "Autism Spectrum Disorder (ASD) is a developmental disability that can cause significant social, communication, and behavioral challenges.",
            "document_id": 1,
            "chunk_index": 0,
            "document_title": "What is Autism",
            "source_url": "https://example.com/autism-basics",
            "metadata": {"category": "basics"}
        },
        {
            "chunk_text": "An Individualized Education Program (IEP) is a legal document that describes how a school will meet a student's unique needs.",
            "document_id": 2,
            "chunk_index": 0,
            "document_title": "IEP Information",
            "source_url": "https://example.com/iep-guide",
            "metadata": {"category": "education"}
        },
        {
            "chunk_text": "Early intervention services for autism can help children develop important skills and improve outcomes.",
            "document_id": 3,
            "chunk_index": 0,
            "document_title": "Early Intervention",
            "source_url": "https://example.com/early-intervention",
            "metadata": {"category": "intervention"}
        }
    ]

    # Generate embeddings and store chunks
    for doc in test_documents:
        embedding = embedding_provider.generate_embedding(doc["chunk_text"])
        doc["embedding"] = embedding

    vector_store.store_document_chunks(test_documents)

    # Now test retrieval
    retrieval_service = factory.get_retrieval_service()
    results = retrieval_service.retrieve_similar_chunks("What is autism?")

    # Check we got results back
    assert isinstance(results, list)
    assert len(results) > 0, "Expected at least one result from retrieval"

    # Check the first result has content
    assert hasattr(results[0], 'chunk_text')
    assert len(results[0].chunk_text) > 0, "Expected chunk_text to not be empty"

    # Verify the most relevant result is about autism
    assert "Autism" in results[0].chunk_text or "autism" in results[0].chunk_text

    print(f"✓ Retrieved {len(results)} results")
    print(f"First result preview: {results[0].chunk_text[:100]}...")
