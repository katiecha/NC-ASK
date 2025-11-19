#!/usr/bin/env python3
"""
Ragas Evaluation Runner for NC-ASK RAG Pipeline

This script provides a convenient command-line interface for running Ragas
evaluations on the NC-ASK RAG pipeline.

Usage:
    # Run basic evaluation (no ground truth required)
    python run_evaluation.py --basic

    # Run comprehensive evaluation (requires ground truth)
    python run_evaluation.py --comprehensive

    # Run specific metrics
    python run_evaluation.py --metrics faithfulness answer_relevancy

    # Run on specific questions
    python run_evaluation.py --questions 1 2 3 5

    # Use specific model for evaluation
    python run_evaluation.py --basic --model gemini-1.5-flash

Examples:
    # Quick evaluation without ground truth
    python run_evaluation.py --basic

    # Full evaluation with all metrics
    python run_evaluation.py --comprehensive

    # Test faithfulness and answer relevancy only
    python run_evaluation.py --metrics faithfulness answer_relevancy
"""
import argparse
import sys
from pathlib import Path
import pytest

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_dir))


def main():
    parser = argparse.ArgumentParser(
        description="Run Ragas evaluation on NC-ASK RAG pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic evaluation (no ground truth required)
  python run_evaluation.py --basic

  # Run comprehensive evaluation (requires ground truth)
  python run_evaluation.py --comprehensive

  # Run specific metrics
  python run_evaluation.py --metrics faithfulness answer_relevancy

  # Use faster model for evaluation
  python run_evaluation.py --basic --model gemini-1.5-flash

Available Metrics:
  - faithfulness: Measures if answers are grounded in contexts (no ground truth)
  - answer_relevancy: Measures if answers are relevant to questions (no ground truth)
  - context_recall: Measures retrieval coverage (requires ground truth)
  - context_precision: Measures ranking quality (requires ground truth)
  - answer_correctness: Measures answer quality (requires ground truth)
        """
    )

    parser.add_argument(
        "--basic",
        action="store_true",
        help="Run basic evaluation without ground truth (faithfulness + answer_relevancy)"
    )

    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive evaluation with all metrics (requires ground truth)"
    )

    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["faithfulness", "answer_relevancy", "context_recall", "context_precision", "answer_correctness"],
        help="Specific metrics to evaluate"
    )

    parser.add_argument(
        "--model",
        default="gemini-1.5-pro",
        choices=["gemini-1.5-pro", "gemini-1.5-flash"],
        help="Gemini model to use for evaluation (default: gemini-1.5-pro)"
    )

    parser.add_argument(
        "--questions",
        nargs="+",
        type=int,
        help="Specific question IDs to evaluate (1-indexed)"
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).parent / "evaluation_datasets" / "qa_golden_dataset.json",
        help="Path to evaluation dataset (default: evaluation_datasets/qa_golden_dataset.json)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "results",
        help="Directory for evaluation results (default: results/)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.basic, args.comprehensive, args.metrics]):
        parser.error("Must specify --basic, --comprehensive, or --metrics")

    if args.basic and args.comprehensive:
        parser.error("Cannot specify both --basic and --comprehensive")

    # Build pytest arguments
    test_file = str(Path(__file__).parent / "test_ragas_evaluation.py")

    # Determine which test to run and build test path
    if args.basic:
        test_path = f"{test_file}::test_basic_metrics_without_ground_truth"
        print("\n" + "="*60)
        print("RUNNING BASIC EVALUATION (No Ground Truth Required)")
        print("="*60)
        print("Metrics: Faithfulness, Answer Relevancy")
        print()

    elif args.comprehensive:
        test_path = f"{test_file}::test_comprehensive_evaluation"
        print("\n" + "="*60)
        print("RUNNING COMPREHENSIVE EVALUATION")
        print("="*60)
        print("Metrics: Faithfulness, Answer Relevancy, Context Recall,")
        print("         Context Precision, Answer Correctness")
        print("\nNote: Requires ground truth answers in dataset")
        print()

    elif args.metrics:
        # Run specific metric tests
        metric_tests = {
            "faithfulness": "test_faithfulness_metric",
            "answer_relevancy": "test_answer_relevancy_metric",
            "context_recall": "test_context_recall_metric",
            "context_precision": "test_context_precision_metric",
            "answer_correctness": "test_answer_correctness_metric",
        }

        print("\n" + "="*60)
        print("RUNNING SPECIFIC METRICS")
        print("="*60)
        print(f"Metrics: {', '.join(args.metrics)}")
        print()

        # Build test path with multiple tests using 'or' syntax
        test_names = [metric_tests[m] for m in args.metrics]
        # For multiple tests, use the 'or' keyword syntax
        test_path = " or ".join([f"{test_file}::{name}" for name in test_names])

    # Build pytest arguments with test path first, then options
    pytest_args = ["-v"]

    if args.verbose:
        pytest_args.append("-s")

    # Add test selection using -k flag for multiple tests, direct path for single test
    if args.metrics:
        # For multiple metrics, use -k with test name pattern
        pytest_args.extend([test_file, "-k", " or ".join(test_names)])
    else:
        # For single test, use direct test path
        pytest_args.insert(0, test_path)

    # Run pytest
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output_dir}")
    print(f"Model: {args.model}")
    print("="*60)
    print()

    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n" + "="*60)
        print("✓ EVALUATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nResults saved to: {args.output_dir}")
        print()
    else:
        print("\n" + "="*60)
        print("✗ EVALUATION FAILED")
        print("="*60)
        print("\nCheck the output above for error details")
        print()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
