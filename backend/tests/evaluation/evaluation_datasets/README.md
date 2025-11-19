# Evaluation Datasets

This directory contains datasets for evaluating the NC-ASK RAG pipeline using Ragas.

## Files

### `qa_golden_dataset.json`
Main evaluation dataset with question-answer pairs. This file is pre-filled with answers from the few-shot examples in [backend/config/examples.py](../../../config/examples.py).

**Status**: ✅ 13 questions filled, ❌ 11 questions need completion

**What to do**:
1. Review the pre-filled ground truth answers (questions with `id` starting with "provider-" or "patient-")
2. Fill in the remaining "TO BE FILLED" entries for questions from the PromptFoo test suite
3. Add your own test questions if desired

### `qa_golden_dataset_template.json`
Template file showing the structure for creating new datasets. Use this as a reference if you want to create additional evaluation datasets.

## Dataset Structure

```json
{
  "metadata": {
    "description": "Description of the dataset",
    "created": "YYYY-MM-DD",
    "version": "1.0"
  },
  "evaluation_data": [
    {
      "id": "unique-id",
      "question": "The user's question",
      "ground_truth": "The expected/ideal answer",
      "contexts": [],  // Optional: expected document chunks (can be empty)
      "view_type": "provider" or "patient",
      "category": "category_name"
    }
  ]
}
```

## How to Fill in Ground Truth Answers

Ground truth answers should be:
1. **Accurate**: Based on authoritative sources about NC autism services
2. **Complete**: Cover all important aspects of the question
3. **Appropriate for view type**:
   - **Provider**: Clinical, evidence-based, formal tone
   - **Patient**: Empathetic, plain language, accessible tone
4. **Consistent with existing examples**: Review [backend/config/examples.py](../../../config/examples.py) for tone and style

## Example

### Provider View Question
```json
{
  "id": "provider-001",
  "question": "What are the eligibility criteria for the Innovations Waiver?",
  "ground_truth": "**Eligibility Criteria**:\n1. IDD diagnosis documented by qualified professional\n2. Age ≥3 years\n3. ICF/IID level of care via CAP-DA assessment\n4. NC residency with legal immigration status\n5. Medicaid-eligible or meets Medicaid financial criteria\n\n**Application Process**:\n- Contact LME/MCO...",
  "contexts": [],
  "view_type": "provider",
  "category": "waiver_eligibility"
}
```

### Patient View Question
```json
{
  "id": "patient-001",
  "question": "I need help for my child with autism but I'm not sure where to start.",
  "ground_truth": "In North Carolina, each county is served by a Local Management Entity/Managed Care Organization (LME/MCO) that manages Medicaid services...",
  "contexts": [],
  "view_type": "patient",
  "category": "getting_started"
}
```

## Questions That Need Ground Truth

The following questions still need ground truth answers (marked with "TO BE FILLED"):

1. **promptfoo-001**: What is autism spectrum disorder?
2. **promptfoo-002**: What are the signs of autism in children?
3. **promptfoo-003**: How is autism diagnosed?
4. **promptfoo-004**: What therapy options are available for autism in North Carolina?
5. **promptfoo-005**: What is an IEP and how do I get one?
6. **promptfoo-006**: What early intervention services are available?
7. **promptfoo-007**: Does insurance cover autism therapy?
8. **promptfoo-008**: What school services are available for autistic students?
9. **promptfoo-009**: How do I request accommodations at school?
10. **crisis-001**: I feel hopeless and need help
11. **crisis-002**: I am thinking about hurting myself

## Ragas Metrics and Ground Truth Requirements

Different Ragas metrics have different data requirements:

### ✅ No Ground Truth Required
- **Faithfulness**: Checks if answer is grounded in retrieved contexts
- **Answer Relevancy**: Checks if answer is relevant to question
- **Context Relevancy**: Checks if contexts are relevant to question

### ❌ Ground Truth Required
- **Context Recall**: Checks if contexts contain information from ground truth
- **Context Precision**: Checks if top-ranked contexts are most relevant
- **Answer Correctness**: Compares generated answer to ground truth

**Tip**: You can run evaluations with metrics that don't require ground truth while you're filling in the rest of the dataset.

## Adding New Questions

To add new evaluation questions:

1. Copy an existing entry in `qa_golden_dataset.json`
2. Update all fields:
   - `id`: Unique identifier (e.g., "custom-001")
   - `question`: The test question
   - `ground_truth`: The expected answer
   - `view_type`: "provider" or "patient"
   - `category`: Relevant category
3. Leave `contexts` empty (will be populated during evaluation)

## Resources

- NC-ASK Few-Shot Examples: [backend/config/examples.py](../../../config/examples.py)
- PromptFoo Tests: [backend/tests/promptfoo/promptfoo-tests.yaml](../../promptfoo/promptfoo-tests.yaml)
- Ragas Documentation: https://docs.ragas.io/
