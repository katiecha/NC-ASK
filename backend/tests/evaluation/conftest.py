"""
Pytest configuration for Ragas evaluation tests.

This module sets up the Ragas evaluation framework with Gemini LLM for evaluating
the NC-ASK RAG pipeline.
"""
import os
import sys

# CRITICAL: Remove mocked ML libraries from parent conftest BEFORE any imports
# The parent conftest.py mocks torch/tensorflow/sentence_transformers as MagicMock
# to speed up unit tests. However, the datasets library (required by Ragas) detects
# these mocked libraries in sys.modules and tries to use them, causing TypeError
# when it tries isinstance() or issubclass() with MagicMock objects.
#
# Solution: Remove the mocks entirely so datasets library doesn't detect them.
for lib_name in ['torch', 'tensorflow', 'sentence_transformers']:
    if lib_name in sys.modules:
        del sys.modules[lib_name]

from pathlib import Path
import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

# Add backend directory to Python path for imports
backend_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_dir))

from services.config import settings
from services.service_factory import ServiceFactory


@pytest.fixture(scope="session")
def ragas_llm():
    """
    Create and configure LLM for Ragas evaluation metrics.

    Uses Google's Gemini model (same as production RAG pipeline).
    Ragas will use this LLM to evaluate faithfulness, answer relevancy, etc.

    Returns:
        ChatGoogleGenerativeAI: Configured Gemini LLM for Ragas
    """
    # Ensure API key is set
    api_key = settings.GOOGLE_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        pytest.skip("GOOGLE_API_KEY not configured. Set it in .env file.")

    # Create Gemini LLM for Ragas evaluation
    # Using gemini-1.5-pro for better evaluation quality
    # (can use gemini-1.5-flash if cost is a concern)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=api_key,
        temperature=0.0,  # Use deterministic evaluation
    )

    return llm


@pytest.fixture(scope="session")
def ragas_embeddings():
    """
    Create embeddings model for Ragas evaluation.

    Uses the same embedding model as production (sentence-transformers).

    Returns:
        Embeddings: Configured embeddings model for Ragas
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    return embeddings


@pytest.fixture(scope="function")
def rag_pipeline():
    """
    Create RAG pipeline instance for evaluation.

    Uses real Supabase vector store with actual ingested documents.
    This provides meaningful evaluation results based on production data.

    Returns:
        RAGPipeline: Configured RAG pipeline for testing

    Note:
        Requires Supabase to be accessible (SUPABASE_URL and keys in .env)
        and documents to be ingested into the vector store.
    """
    factory = ServiceFactory(use_in_memory_store=False)
    pipeline = factory.create_rag_pipeline()

    return pipeline


@pytest.fixture(scope="session")
def golden_dataset_path():
    """
    Path to the golden dataset for evaluation.

    Returns:
        Path: Path to qa_golden_dataset.json
    """
    dataset_path = Path(__file__).parent / "evaluation_datasets" / "qa_golden_dataset.json"

    if not dataset_path.exists():
        pytest.skip(f"Golden dataset not found at {dataset_path}")

    return dataset_path


@pytest.fixture(scope="session")
def evaluation_results_dir():
    """
    Directory for storing evaluation results.

    Returns:
        Path: Path to results directory
    """
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    return results_dir


# Ragas configuration constants
RAGAS_METRICS_CONFIG = {
    "faithfulness": {
        "description": "Measures if the answer is grounded in the retrieved contexts",
        "requires_ground_truth": False,
        "range": "0-1 (higher is better)",
    },
    "answer_relevancy": {
        "description": "Measures how relevant the answer is to the question",
        "requires_ground_truth": False,
        "range": "0-1 (higher is better)",
    },
    "context_recall": {
        "description": "Measures if all relevant information from ground truth is in contexts",
        "requires_ground_truth": True,
        "range": "0-1 (higher is better)",
    },
    "context_precision": {
        "description": "Measures if top-ranked contexts are most relevant",
        "requires_ground_truth": True,
        "range": "0-1 (higher is better)",
    },
    "answer_correctness": {
        "description": "Measures overall answer quality vs ground truth",
        "requires_ground_truth": True,
        "range": "0-1 (higher is better)",
    },
    "context_relevancy": {
        "description": "Measures if retrieved contexts are relevant to the question",
        "requires_ground_truth": False,
        "range": "0-1 (higher is better)",
    },
}
