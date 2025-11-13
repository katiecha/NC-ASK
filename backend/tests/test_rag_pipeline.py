import pytest

from services.service_factory import ServiceFactory


@pytest.mark.asyncio
async def test_rag_pipeline():
    """Test RAG pipeline returns valid response."""
    # Use in-memory vector store to avoid real Supabase connection
    factory = ServiceFactory(use_in_memory_store=True)
    pipeline = factory.create_rag_pipeline()

    result = await pipeline.process_query("What resources are available for autism support?")

    assert "response" in result
    assert "citations" in result
    assert "crisis_detected" in result
    assert isinstance(result["response"], str)
    assert len(result["response"]) > 0
