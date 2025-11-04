from services.service_factory import ServiceFactory


def test_retrieval_service():
    """Test retrieval service returns results."""
    # Use in-memory vector store to avoid real Supabase connection
    factory = ServiceFactory(use_in_memory_store=True)
    retrieval_service = factory.get_retrieval_service()

    results = retrieval_service.retrieve_similar_chunks("What is autism?")

    # Check we got results back
    assert isinstance(results, list)
    assert len(results) > 0, "Expected at least one result from retrieval"

    # Check the first result has content
    assert hasattr(results[0], 'chunk_text')
    assert len(results[0].chunk_text) > 0, "Expected chunk_text to not be empty"

    print(f"✓ Retrieved {len(results)} results")
    print(f"First result preview: {results[0].chunk_text[:100]}...")
