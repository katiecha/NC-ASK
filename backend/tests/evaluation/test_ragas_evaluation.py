"""
Ragas evaluation tests for NC-ASK RAG pipeline.

This module implements comprehensive evaluation of the RAG pipeline using Ragas metrics:
- Faithfulness: Measures if answers are grounded in retrieved contexts
- Answer Relevancy: Measures if answers are relevant to questions
- Context Relevancy: Measures if retrieved contexts are relevant to questions
- Context Recall: Measures if contexts contain all relevant information from ground truth
- Context Precision: Measures if top-ranked contexts are most relevant
- Answer Correctness: Measures overall answer quality vs ground truth

Usage:
    # Run all evaluations
    pytest backend/tests/evaluation/test_ragas_evaluation.py -v

    # Run only metrics that don't require ground truth
    pytest backend/tests/evaluation/test_ragas_evaluation.py -v -m "not requires_ground_truth"

    # Run only faithfulness evaluation
    pytest backend/tests/evaluation/test_ragas_evaluation.py::test_faithfulness_metric -v
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_correctness,
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

# Note: context_relevancy was renamed to context_entity_recall in newer versions
# We'll use a custom implementation if needed
try:
    from ragas.metrics import context_relevancy
except ImportError:
    # If context_relevancy is not available, we'll skip it
    context_relevancy = None


class RagasEvaluator:
    """
    Evaluator for NC-ASK RAG pipeline using Ragas metrics.
    """

    def __init__(self, rag_pipeline, llm, embeddings, results_dir: Path):
        """
        Initialize the evaluator.

        Args:
            rag_pipeline: RAG pipeline instance to evaluate
            llm: LLM for Ragas evaluation
            embeddings: Embeddings model for Ragas evaluation
            results_dir: Directory to save evaluation results
        """
        self.rag_pipeline = rag_pipeline
        self.llm = llm
        self.embeddings = embeddings
        self.results_dir = results_dir

    def load_dataset(self, dataset_path: Path, skip_incomplete: bool = False) -> list[dict]:
        """
        Load golden dataset from JSON file.

        Args:
            dataset_path: Path to qa_golden_dataset.json
            skip_incomplete: If True, skip entries with "TO BE FILLED" ground truth

        Returns:
            List of dataset entries
        """
        with open(dataset_path) as f:
            data = json.load(f)

        entries = data["evaluation_data"]

        if skip_incomplete:
            entries = [
                e for e in entries
                if e.get("ground_truth") and "TO BE FILLED" not in e["ground_truth"]
            ]

        return entries

    async def run_rag_pipeline(self, question: str, view_type: str = "patient") -> dict[str, Any]:
        """
        Run the RAG pipeline for a given question.

        Args:
            question: User question
            view_type: "provider" or "patient"

        Returns:
            Dict with answer, contexts, and metadata
        """
        result = await self.rag_pipeline.process_query(
            query=question,
            session_id=None,
            view_type=view_type
        )

        # Extract contexts from retrieval results
        # Note: We need to access the retrieval results from the pipeline
        # For now, we'll use a workaround by re-running retrieval
        retrieval_service = self.rag_pipeline.retrieval_service

        # Get retrieval results
        retrieval_results = retrieval_service.retrieve_similar_chunks(
            query=question,
            top_k=5
        )

        contexts = [r.chunk_text for r in retrieval_results]

        return {
            "answer": result["response"],
            "contexts": contexts,
            "citations": result.get("citations", []),
            "crisis_detected": result.get("crisis_detected", False),
        }

    async def prepare_ragas_dataset(
        self,
        dataset_entries: list[dict],
        include_ground_truth: bool = True
    ) -> Dataset:
        """
        Prepare dataset in Ragas format.

        Args:
            dataset_entries: List of dataset entries from JSON
            include_ground_truth: Whether to include ground truth (needed for some metrics)

        Returns:
            Ragas Dataset with question, answer, contexts, and optionally ground_truth
        """
        ragas_data = {
            "question": [],
            "answer": [],
            "contexts": [],
        }

        if include_ground_truth:
            ragas_data["ground_truth"] = []

        for entry in dataset_entries:
            question = entry["question"]
            view_type = entry.get("view_type", "patient")

            # Run RAG pipeline
            print(f"Running RAG for: {question[:50]}...")
            result = await self.run_rag_pipeline(question, view_type)

            ragas_data["question"].append(question)
            ragas_data["answer"].append(result["answer"])
            ragas_data["contexts"].append(result["contexts"])

            if include_ground_truth:
                ragas_data["ground_truth"].append(entry["ground_truth"])

        return Dataset.from_dict(ragas_data)

    def evaluate_metrics(
        self,
        dataset: Dataset,
        metrics: list,
        run_name: str = "evaluation"
    ) -> dict:
        """
        Evaluate dataset with specified Ragas metrics.

        Args:
            dataset: Ragas dataset
            metrics: List of Ragas metrics to evaluate
            run_name: Name for this evaluation run

        Returns:
            Evaluation results
        """
        print(f"\nRunning Ragas evaluation: {run_name}")
        print(f"Metrics: {[m.name for m in metrics]}")
        print(f"Dataset size: {len(dataset)}")

        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=self.llm,
            embeddings=self.embeddings,
        )

        return result

    def save_results(self, results: dict, metrics_names: list[str], run_name: str):
        """
        Save evaluation results to JSON file.

        Args:
            results: Evaluation results from Ragas
            metrics_names: Names of evaluated metrics
            run_name: Name of the evaluation run
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ragas_{run_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        output = {
            "run_name": run_name,
            "timestamp": timestamp,
            "metrics": metrics_names,
            "results": results,
            "summary": {
                metric: float(results[metric]) if metric in results else None
                for metric in metrics_names
            }
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"\nResults saved to: {filepath}")

        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        for metric, score in output["summary"].items():
            if score is not None:
                print(f"{metric:25s}: {score:.4f}")
        print("="*60)


# ============================================================================
# Test Cases
# ============================================================================


@pytest.mark.asyncio
async def test_faithfulness_metric(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Test Faithfulness metric.

    Faithfulness measures whether the generated answer is grounded in the
    retrieved contexts. Higher scores indicate better factual consistency.

    Does NOT require ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset (can include entries without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=False)

    # Prepare dataset (no ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=False)

    # Evaluate
    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=[faithfulness],
        run_name="faithfulness"
    )

    # Save results
    evaluator.save_results(results, ["faithfulness"], "faithfulness")

    # Assert minimum quality threshold
    assert results["faithfulness"] > 0.5, \
        f"Faithfulness score too low: {results['faithfulness']:.4f}"


@pytest.mark.asyncio
async def test_answer_relevancy_metric(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Test Answer Relevancy metric.

    Answer Relevancy measures how relevant the generated answer is to the
    question. Higher scores indicate better relevance.

    Does NOT require ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=False)

    # Prepare dataset (no ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=False)

    # Evaluate
    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=[answer_relevancy],
        run_name="answer_relevancy"
    )

    # Save results
    evaluator.save_results(results, ["answer_relevancy"], "answer_relevancy")

    # Assert minimum quality threshold
    assert results["answer_relevancy"] > 0.6, \
        f"Answer Relevancy score too low: {results['answer_relevancy']:.4f}"


@pytest.mark.requires_ground_truth
@pytest.mark.asyncio
async def test_context_recall_metric(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Test Context Recall metric.

    Context Recall measures whether the retrieved contexts contain all
    relevant information from the ground truth. Higher scores indicate
    better retrieval coverage.

    REQUIRES ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset (skip entries without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=True)

    if len(dataset_entries) == 0:
        pytest.skip("No complete ground truth entries available")

    # Prepare dataset (ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=True)

    # Evaluate
    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=[context_recall],
        run_name="context_recall"
    )

    # Save results
    evaluator.save_results(results, ["context_recall"], "context_recall")

    # Assert minimum quality threshold
    assert results["context_recall"] > 0.5, \
        f"Context Recall score too low: {results['context_recall']:.4f}"


@pytest.mark.requires_ground_truth
@pytest.mark.asyncio
async def test_context_precision_metric(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Test Context Precision metric.

    Context Precision measures whether the top-ranked contexts are the most
    relevant ones. Higher scores indicate better ranking quality.

    REQUIRES ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset (skip entries without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=True)

    if len(dataset_entries) == 0:
        pytest.skip("No complete ground truth entries available")

    # Prepare dataset (ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=True)

    # Evaluate
    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=[context_precision],
        run_name="context_precision"
    )

    # Save results
    evaluator.save_results(results, ["context_precision"], "context_precision")

    # Assert minimum quality threshold
    assert results["context_precision"] > 0.5, \
        f"Context Precision score too low: {results['context_precision']:.4f}"


@pytest.mark.requires_ground_truth
@pytest.mark.asyncio
async def test_answer_correctness_metric(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Test Answer Correctness metric.

    Answer Correctness measures the overall quality of the generated answer
    compared to the ground truth. It considers both factual and semantic
    correctness. Higher scores indicate better answer quality.

    REQUIRES ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset (skip entries without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=True)

    if len(dataset_entries) == 0:
        pytest.skip("No complete ground truth entries available")

    # Prepare dataset (ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=True)

    # Evaluate
    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=[answer_correctness],
        run_name="answer_correctness"
    )

    # Save results
    evaluator.save_results(results, ["answer_correctness"], "answer_correctness")

    # Assert minimum quality threshold
    assert results["answer_correctness"] > 0.5, \
        f"Answer Correctness score too low: {results['answer_correctness']:.4f}"


@pytest.mark.asyncio
async def test_comprehensive_evaluation(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Run comprehensive evaluation with all metrics.

    This test runs all Ragas metrics together for a complete evaluation.
    Only runs on entries with complete ground truth.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load dataset (skip entries without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=True)

    if len(dataset_entries) == 0:
        pytest.skip("No complete ground truth entries available")

    # Prepare dataset (ground truth needed for comprehensive evaluation)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=True)

    # Evaluate with all metrics
    all_metrics = [
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
        answer_correctness,
    ]

    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=all_metrics,
        run_name="comprehensive"
    )

    # Save results
    metric_names = [m.name for m in all_metrics]
    evaluator.save_results(results, metric_names, "comprehensive")

    # Assert all metrics meet minimum thresholds
    assert results["faithfulness"] > 0.5
    assert results["answer_relevancy"] > 0.6
    assert results["context_recall"] > 0.5
    assert results["context_precision"] > 0.5
    assert results["answer_correctness"] > 0.5


@pytest.mark.asyncio
async def test_basic_metrics_without_ground_truth(
    rag_pipeline,
    ragas_llm,
    ragas_embeddings,
    golden_dataset_path,
    evaluation_results_dir
):
    """
    Run basic evaluation without ground truth.

    This test can be run immediately without filling in ground truth answers.
    It evaluates:
    - Faithfulness
    - Answer Relevancy

    These metrics only require questions and don't need reference answers.
    """
    evaluator = RagasEvaluator(
        rag_pipeline=rag_pipeline,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        results_dir=evaluation_results_dir
    )

    # Load ALL dataset entries (including those without ground truth)
    dataset_entries = evaluator.load_dataset(golden_dataset_path, skip_incomplete=False)

    # Prepare dataset (no ground truth needed)
    dataset = await evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=False)

    # Evaluate with metrics that don't require ground truth
    basic_metrics = [
        faithfulness,
        answer_relevancy,
    ]

    results = evaluator.evaluate_metrics(
        dataset=dataset,
        metrics=basic_metrics,
        run_name="basic_no_ground_truth"
    )

    # Save results
    metric_names = [m.name for m in basic_metrics]
    evaluator.save_results(results, metric_names, "basic_no_ground_truth")

    print("\nℹ️  This evaluation ran on ALL questions, including those without ground truth.")
    print("   To run advanced metrics (context recall, context precision, answer correctness),")
    print("   fill in the ground truth answers in qa_golden_dataset.json")

    # Assert metrics meet minimum thresholds
    assert results["faithfulness"] > 0.5
    assert results["answer_relevancy"] > 0.6
