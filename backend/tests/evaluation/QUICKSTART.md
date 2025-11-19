# Ragas Evaluation - Quick Start Guide

This guide will get you up and running with Ragas evaluation in under 5 minutes.

## Prerequisites

- Python environment with dependencies installed
- Google API key configured in `.env`
- Backend running (for testing with live data) or using in-memory store (for testing without database)

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `ragas` - Evaluation framework
- `langchain-google-genai` - Gemini integration
- `langchain-community` - Embeddings support
- `datasets` - Dataset handling

## Step 2: Run Your First Evaluation

### Option A: Using NPM Scripts (Recommended)

```bash
# From project root
npm run evaluate:ragas
```

This runs a basic evaluation with **faithfulness** and **answer relevancy** metrics.

### Option B: Using Python Directly

```bash
cd backend/tests/evaluation
python run_evaluation.py --basic
```

## Step 3: View Results

Results are saved to `backend/tests/evaluation/results/` as JSON files with timestamps.

### Generate HTML Report

```bash
npm run evaluate:ragas:report
```

Then open the generated HTML file in your browser:

```bash
open backend/tests/evaluation/results/report_*.html
```

## What Just Happened?

The evaluation:

1. ✅ Loaded 24 test questions from the golden dataset
2. ✅ Ran each question through your RAG pipeline
3. ✅ Evaluated faithfulness (are answers grounded in contexts?)
4. ✅ Evaluated answer relevancy (do answers address the questions?)
5. ✅ Saved results to JSON and generated a report

## Understanding Your Results

| Metric | Score | What It Means |
|--------|-------|---------------|
| **Faithfulness** | 0.0-1.0 | How well answers stay within retrieved contexts |
| **Answer Relevancy** | 0.0-1.0 | How well answers address the questions |

**Score Interpretation**:
- **0.7-1.0**: ✅ Excellent
- **0.5-0.7**: ⚠️ Good (room for improvement)
- **0.0-0.5**: ❌ Needs work

## Next Steps

### 1. Fill in Ground Truth Answers (Optional but Recommended)

For advanced metrics (context recall, context precision, answer correctness), you need ground truth answers.

**Status**: 13/24 questions have ground truth, 11 need completion

**How to fill**:

1. Open [evaluation_datasets/qa_golden_dataset.json](evaluation_datasets/qa_golden_dataset.json)
2. Find entries with `"TO BE FILLED"` in the `ground_truth` field
3. Replace with accurate, complete answers
4. See [evaluation_datasets/README.md](evaluation_datasets/README.md) for guidelines

### 2. Run Comprehensive Evaluation

Once ground truth is complete:

```bash
npm run evaluate:ragas:comprehensive
```

This evaluates **all 5 metrics**:
- ✅ Faithfulness
- ✅ Answer Relevancy
- ✅ Context Recall (requires ground truth)
- ✅ Context Precision (requires ground truth)
- ✅ Answer Correctness (requires ground truth)

### 3. Iterate and Improve

Based on evaluation results:

1. **Low Faithfulness?** → Improve prompts to stay grounded in context
2. **Low Answer Relevancy?** → Refine prompts to better address questions
3. **Low Context Recall?** → Increase `TOP_K_RETRIEVAL` or adjust chunking
4. **Low Context Precision?** → Improve ranking/re-ranking strategies
5. **Low Answer Correctness?** → Review overall system (prompts, retrieval, sources)

## Common Commands

```bash
# Basic evaluation (no ground truth needed)
npm run evaluate:ragas

# Comprehensive evaluation (requires ground truth)
npm run evaluate:ragas:comprehensive

# Generate HTML report
npm run evaluate:ragas:report

# Run specific metrics
cd backend/tests/evaluation
python run_evaluation.py --metrics faithfulness answer_relevancy

# Use faster model (lower cost, faster)
python run_evaluation.py --basic --model gemini-1.5-flash

# Verbose output
python run_evaluation.py --basic -v
```

## Troubleshooting

### "GOOGLE_API_KEY not configured"

Add your API key to `.env`:

```bash
echo 'GOOGLE_API_KEY=your_actual_key_here' >> .env
```

### "No module named 'ragas'"

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Tests are slow

Use the faster model:

```bash
python run_evaluation.py --basic --model gemini-1.5-flash
```

## Need More Help?

- **Full Documentation**: [README.md](README.md)
- **Dataset Guide**: [evaluation_datasets/README.md](evaluation_datasets/README.md)
- **Ragas Docs**: https://docs.ragas.io/

---

**You're all set! 🎉 Happy evaluating!**
