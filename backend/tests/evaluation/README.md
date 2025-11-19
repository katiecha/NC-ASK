# Ragas Evaluation for NC-ASK RAG Pipeline

Comprehensive evaluation framework for the NC-ASK RAG pipeline using [Ragas](https://docs.ragas.io/), a framework specifically designed for evaluating Retrieval-Augmented Generation systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running Evaluations](#running-evaluations)
- [Understanding Metrics](#understanding-metrics)
- [Ground Truth Dataset](#ground-truth-dataset)
- [Generating Reports](#generating-reports)
- [Advanced Usage](#advanced-usage)
- [Interpreting Results](#interpreting-results)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

This evaluation framework measures the quality of the NC-ASK RAG pipeline across multiple dimensions:

- **Faithfulness**: Are answers grounded in retrieved contexts?
- **Answer Relevancy**: Do answers address the questions asked?
- **Context Recall**: Does retrieval find all relevant information?
- **Context Precision**: Are the most relevant contexts ranked highest?
- **Answer Correctness**: How accurate are answers vs ground truth?

## ⚡ Quick Start

### Run Basic Evaluation (No Ground Truth Required)

```bash
# From project root
npm run evaluate:ragas
```

This runs faithfulness and answer relevancy metrics on all questions in the dataset, including those without ground truth answers.

### Run Comprehensive Evaluation (Requires Ground Truth)

```bash
npm run evaluate:ragas:comprehensive
```

This runs all metrics but only on questions that have ground truth answers filled in.

### Generate HTML Report

```bash
npm run evaluate:ragas:report
```

This generates a visual HTML report from the latest evaluation results.

## 📦 Installation

### 1. Install Ragas

Ragas has already been added to `requirements.txt`. Install it with:

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `ragas>=0.1.0` - Main evaluation framework
- `langchain-google-genai` - For using Gemini with Ragas
- `datasets` - For handling evaluation datasets

### 2. Configure API Keys

Ensure your `.env` file in the project root has the Google API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

Ragas uses this key to run evaluation metrics with Gemini.

### 3. Verify Installation

```bash
cd backend/tests/evaluation
python -c "import ragas; print('Ragas installed successfully!')"
```

## 🚀 Running Evaluations

### Using NPM Scripts (Recommended)

```bash
# Basic evaluation (faithfulness + answer relevancy)
npm run evaluate:ragas

# Comprehensive evaluation (all metrics)
npm run evaluate:ragas:comprehensive

# Generate HTML report from latest results
npm run evaluate:ragas:report
```

### Using Python Scripts Directly

```bash
cd backend/tests/evaluation

# Basic evaluation
python run_evaluation.py --basic

# Comprehensive evaluation
python run_evaluation.py --comprehensive

# Specific metrics
python run_evaluation.py --metrics faithfulness answer_relevancy

# Use faster model
python run_evaluation.py --basic --model gemini-1.5-flash

# Verbose output
python run_evaluation.py --basic -v
```

### Using Pytest Directly

```bash
cd backend

# Run all evaluation tests
pytest tests/evaluation/test_ragas_evaluation.py -v

# Run specific metric test
pytest tests/evaluation/test_ragas_evaluation.py::test_faithfulness_metric -v

# Run only tests that don't require ground truth
pytest tests/evaluation/test_ragas_evaluation.py -v -m "not requires_ground_truth"

# Run with verbose output
pytest tests/evaluation/test_ragas_evaluation.py -v -s
```

## 📊 Understanding Metrics

### Metrics That DON'T Require Ground Truth

These can be run immediately without filling in reference answers:

#### 1. **Faithfulness** (0-1, higher is better)

**What it measures**: Whether the generated answer is grounded in the retrieved contexts.

**Why it matters**: Prevents hallucinations and ensures answers are based on actual source material.

**Example**:
- **Context**: "The Innovations Waiver requires age ≥3 years"
- **High Faithfulness**: "The Innovations Waiver is available for individuals aged 3 and older"
- **Low Faithfulness**: "The Innovations Waiver is available for all ages" (contradicts context)

**Threshold**: Aim for ≥ 0.7

#### 2. **Answer Relevancy** (0-1, higher is better)

**What it measures**: Whether the answer is relevant to the question asked.

**Why it matters**: Ensures the system addresses what users actually want to know.

**Example**:
- **Question**: "What is an IEP?"
- **High Relevancy**: "An IEP (Individualized Education Program) is a legal document..."
- **Low Relevancy**: "Schools provide many services..." (too vague, doesn't define IEP)

**Threshold**: Aim for ≥ 0.7

### Metrics That REQUIRE Ground Truth

Fill in ground truth answers in [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json) to use these:

#### 3. **Context Recall** (0-1, higher is better)

**What it measures**: Whether the retrieved contexts contain all relevant information from the ground truth.

**Why it matters**: Indicates if your retrieval system is finding the right documents.

**Low scores suggest**: Increasing `TOP_K_RETRIEVAL`, adjusting chunk size, or improving embedding model.

**Threshold**: Aim for ≥ 0.6

#### 4. **Context Precision** (0-1, higher is better)

**What it measures**: Whether the most relevant contexts are ranked highest.

**Why it matters**: Better ranking means the LLM sees the most important information first.

**Low scores suggest**: Adjusting similarity thresholds or implementing re-ranking.

**Threshold**: Aim for ≥ 0.6

#### 5. **Answer Correctness** (0-1, higher is better)

**What it measures**: Overall answer quality compared to ground truth (factual + semantic).

**Why it matters**: Holistic measure of system performance.

**Low scores suggest**: Improving prompts, retrieval, or source document quality.

**Threshold**: Aim for ≥ 0.6

## 📝 Ground Truth Dataset

### Current Status

**Location**: [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json)

**Status**:
- ✅ **13 questions** pre-filled from few-shot examples
- ❌ **11 questions** need ground truth answers (marked "TO BE FILLED")

### Filling in Ground Truth

1. **Open the dataset**: [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json)

2. **Find entries marked "TO BE FILLED"**:
   ```json
   {
     "id": "promptfoo-001",
     "question": "What is autism spectrum disorder?",
     "ground_truth": "TO BE FILLED - Add comprehensive definition...",
     ...
   }
   ```

3. **Replace with accurate answers**:
   ```json
   {
     "id": "promptfoo-001",
     "question": "What is autism spectrum disorder?",
     "ground_truth": "Autism Spectrum Disorder (ASD) is a developmental disability caused by differences in the brain. People with ASD may communicate, interact, behave, and learn in ways that are different from most other people...",
     ...
   }
   ```

4. **Guidelines**:
   - Match the view type (provider = clinical, patient = empathetic)
   - Base answers on authoritative NC autism service sources
   - See [evaluation_datasets/README.md](evaluation_datasets/README.md) for detailed guidelines

### Reference Sources

Use these existing examples as templates:
- **Provider examples**: [backend/config/examples.py](../../config/examples.py) (lines 26-77)
- **Patient examples**: [backend/config/examples.py](../../config/examples.py) (lines 84-145)

## 📈 Generating Reports

### Generate HTML Report

```bash
npm run evaluate:ragas:report
```

Or with Python:

```bash
cd backend/tests/evaluation
python generate_report.py
```

This generates a visual HTML report with:
- Metric scores and progress bars
- Color-coded performance indicators
- Detailed interpretations
- Actionable recommendations

Reports are saved to [results/](results/) with timestamps.

### View Report

```bash
# Open latest report in browser (macOS)
open backend/tests/evaluation/results/report_*.html

# Linux
xdg-open backend/tests/evaluation/results/report_*.html

# Windows
start backend/tests/evaluation/results/report_*.html
```

## 🔧 Advanced Usage

### Evaluate Specific Questions

```python
cd backend/tests/evaluation
python run_evaluation.py --basic --questions 1 2 3 5
```

### Custom Dataset

```bash
python run_evaluation.py --basic --dataset path/to/custom_dataset.json
```

### Custom Output Directory

```bash
python run_evaluation.py --basic --output-dir /path/to/results
```

### Programmatic Usage

```python
from pathlib import Path
from test_ragas_evaluation import RagasEvaluator
from conftest import ragas_llm, ragas_embeddings
from services.service_factory import ServiceFactory

# Create RAG pipeline
factory = ServiceFactory(use_in_memory_store=True)
pipeline = factory.get_rag_pipeline()

# Create evaluator
evaluator = RagasEvaluator(
    rag_pipeline=pipeline,
    llm=ragas_llm(),
    embeddings=ragas_embeddings(),
    results_dir=Path("results")
)

# Load and evaluate
dataset_entries = evaluator.load_dataset(
    Path("evaluation_datasets/qa_golden_dataset.json"),
    skip_incomplete=True
)
dataset = evaluator.prepare_ragas_dataset(dataset_entries, include_ground_truth=True)

# Run evaluation
from ragas.metrics import faithfulness, answer_relevancy
results = evaluator.evaluate_metrics(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy],
    run_name="custom_eval"
)

print(results)
```

## 📊 Interpreting Results

### Score Ranges

| Score | Rating | Meaning |
|-------|--------|---------|
| 0.7 - 1.0 | ✅ Excellent | System performing very well |
| 0.5 - 0.7 | ⚠️ Good | Adequate performance, room for improvement |
| 0.0 - 0.5 | ❌ Poor | Needs significant improvement |

### Common Issues and Solutions

#### Low Faithfulness (< 0.6)

**Problem**: Answers not grounded in retrieved contexts.

**Solutions**:
- Strengthen prompts to emphasize staying within provided context
- Add explicit instructions to cite sources
- Review and improve source document quality
- Check if retrieval is returning relevant contexts

#### Low Answer Relevancy (< 0.6)

**Problem**: Answers don't address the questions.

**Solutions**:
- Improve prompt engineering for better instruction following
- Add query expansion or reformulation
- Review few-shot examples for better guidance
- Check if questions are being processed correctly

#### Low Context Recall (< 0.5)

**Problem**: Retrieval missing relevant information.

**Solutions**:
- Increase `TOP_K_RETRIEVAL` in [backend/services/config.py](../../services/config.py)
- Experiment with different chunk sizes (`CHUNK_SIZE`, `CHUNK_OVERLAP`)
- Consider using a different embedding model
- Review document preprocessing and chunking strategy

#### Low Context Precision (< 0.5)

**Problem**: Most relevant contexts not ranked highest.

**Solutions**:
- Adjust similarity score thresholds
- Implement re-ranking strategies
- Use a more powerful embedding model
- Consider hybrid search (keyword + semantic)

#### Low Answer Correctness (< 0.5)

**Problem**: Generated answers differ significantly from ground truth.

**Solutions**:
- Review and improve prompt templates
- Ensure ground truth answers are accurate and complete
- Check if the LLM model is appropriate for the task
- Verify that retrieval is finding the right documents

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not configured"

**Solution**: Set your Google API key in the `.env` file:

```bash
echo 'GOOGLE_API_KEY=your_actual_key' >> .env
```

### "No complete ground truth entries available"

**Solution**: Fill in ground truth answers in [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json). See [Ground Truth Dataset](#ground-truth-dataset) section.

### "ModuleNotFoundError: No module named 'ragas'"

**Solution**: Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Tests run very slowly

**Solution**: Use the faster Gemini model:

```bash
python run_evaluation.py --basic --model gemini-1.5-flash
```

Or reduce the number of test questions by editing the dataset.

### Import errors when running tests

**Solution**: Make sure you're running from the correct directory:

```bash
# Correct
cd backend
pytest tests/evaluation/test_ragas_evaluation.py -v

# Or use npm scripts from project root
npm run evaluate:ragas
```

## 📁 Directory Structure

```
backend/tests/evaluation/
├── README.md                          # This file
├── conftest.py                        # Pytest configuration and fixtures
├── test_ragas_evaluation.py          # Main evaluation test suite
├── run_evaluation.py                  # CLI runner script
├── generate_report.py                 # HTML report generator
├── evaluation_datasets/
│   ├── README.md                      # Dataset documentation
│   ├── qa_golden_dataset.json        # Main evaluation dataset
│   └── qa_golden_dataset_template.json # Template for new datasets
└── results/                           # Evaluation results (generated)
    ├── ragas_*.json                   # JSON results
    └── report_*.html                  # HTML reports
```

## 🔗 Related Documentation

- [Ragas Official Documentation](https://docs.ragas.io/)
- [NC-ASK Few-Shot Examples](../../config/examples.py)
- [PromptFoo Tests](../promptfoo/promptfoo-tests.yaml)
- [RAG Pipeline Documentation](../../services/rag_pipeline.py)

## 📝 Next Steps

1. **Fill in ground truth answers** in [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json) for the remaining 11 questions
2. **Run basic evaluation** to establish baseline metrics: `npm run evaluate:ragas`
3. **Run comprehensive evaluation** once ground truth is complete: `npm run evaluate:ragas:comprehensive`
4. **Generate and review HTML report**: `npm run evaluate:ragas:report`
5. **Iterate and improve** based on results and recommendations
6. **Re-run periodically** to track improvements and catch regressions

## 🤝 Contributing

When adding new evaluation questions:

1. Add them to [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json)
2. Follow the structure in the template
3. Include ground truth answers for comprehensive metrics
4. Categorize appropriately (provider/patient, category tags)
5. Document any special considerations

## 📧 Questions or Issues?

If you encounter issues or have questions about Ragas evaluation:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [Ragas documentation](https://docs.ragas.io/)
3. Examine test output for specific error messages
4. Consult the team or create an issue in the project repository

---

**Happy Evaluating! 🎯**
