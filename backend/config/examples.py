"""
Few-shot examples for LLM prompting.

This module contains example query-response pairs that demonstrate the desired
tone and style for each view type. These examples are included in the LLM prompt
to guide response generation through in-context learning.

You can update these examples based on actual user queries and optimal responses.
"""
from typing import TypedDict, List, Literal

ViewType = Literal["provider", "patient"]


class Example(TypedDict):
    """Structure for a single example query-response pair"""
    query: str
    response: str


# ============================================================================
# Healthcare Provider Examples (Clinical, Evidence-Based Tone)
# ============================================================================

PROVIDER_EXAMPLES: List[Example] = [
    {
        "query": "What are the eligibility criteria for the Innovations Waiver?",
        "response": """The Innovations Waiver eligibility criteria include:

1. **Diagnosis Requirement**: Intellectual/developmental disability (IDD) diagnosis documented by qualified professional
2. **Age**: Must be 3 years or older
3. **Functional Assessment**: ICF/IID level of care determination via CAP-DA assessment
4. **Residency**: North Carolina resident with legal immigration status
5. **Medicaid**: Must be Medicaid-eligible or meet Medicaid financial criteria

**Application Process**:
- Contact Local Management Entity/Managed Care Organization (LME/MCO)
- Complete CAP-DA assessment
- Slot assignment from waitlist based on priority population status

**Contact**: Alliance Health: 1-800-510-9132 | Vaya Health: 1-800-849-6127

**Note**: This is general eligibility information. Individual patient circumstances require case-by-case evaluation by the LME/MCO."""
    },
    {
        "query": "How do I refer a patient for IEP evaluation?",
        "response": """IEP evaluation referral process per IDEA regulations:

**Referral Steps**:
1. Submit written referral to school principal or Director of Exceptional Children
2. Include specific educational concerns and supporting documentation
3. Request comprehensive psychoeducational evaluation under IDEA

**Required Timeline**:
- School must respond within 10 business days
- Evaluation must be completed within 90 days of parental consent

**Evaluation Domains** (as clinically indicated):
- Cognitive functioning
- Academic achievement
- Communication skills
- Motor skills
- Behavioral/emotional functioning
- Adaptive behavior

**Clinical Documentation**: Provide relevant medical records, developmental history, and diagnostic reports to support referral.

**Parent Rights**: Parents must receive prior written notice and consent before evaluation begins (34 CFR §300.304).

Refer families to NC Department of Public Instruction Exceptional Children Division for procedural guidance: 919-807-3969."""
    },
    {
        "query": "What medications are covered for autism treatment?",
        "response": """Medication coverage for autism spectrum disorder varies by insurance plan and clinical indication.

**NC Medicaid Coverage**:
Medications must be FDA-approved for specific indications and medically necessary. Common covered categories include:
- Atypical antipsychotics (risperidone, aripiprazole) for irritability/aggression
- SSRIs for co-morbid anxiety/OCD
- Stimulants/atomoxetine for co-morbid ADHD
- Sleep medications for documented sleep disorders

**Prior Authorization**: May be required for certain medications. Submit clinical documentation supporting medical necessity.

**Important Clinical Considerations**:
- No medications are FDA-approved to treat core autism symptoms
- Pharmacotherapy targets specific behavioral or psychiatric co-morbidities
- Evidence-based behavioral interventions remain first-line treatment

**Recommendation**: Consult patient's insurance formulary and prior authorization requirements. Consider referral to developmental-behavioral pediatrician or child psychiatrist for medication management.

This is general information only. Prescribing decisions must be based on individual patient assessment and clinical judgment."""
    },
]


# ============================================================================
# Patient/Parent Examples (Empathetic, Plain Language Tone)
# ============================================================================

PATIENT_EXAMPLES: List[Example] = [
    {
        "query": "What are the eligibility criteria for the Innovations Waiver?",
        "response": """The Innovations Waiver helps families get services for their child with autism. Here's what your child needs to qualify:

**Who Can Get It**:
- Children 3 years or older
- Has an autism or developmental disability diagnosis
- Lives in North Carolina
- Qualifies for Medicaid (or meets income requirements)

**How to Apply**:
1. Call your local care coordinator (we can help you find them)
2. They'll set up an assessment to see what services your child needs
3. Your child will be placed on a waitlist

**Important to Know**: There is a waitlist for this program. Some families get priority based on their child's needs.

**Need Help Getting Started?**
- Alliance Health: 1-800-510-9132
- Vaya Health: 1-800-849-6127

The people at these organizations are there to help you through the process. Don't hesitate to call with questions."""
    },
    {
        "query": "How do I get my child evaluated for an IEP?",
        "response": """Getting your child evaluated for an IEP is simpler than it sounds. Here's what to do:

**Step 1: Write a Letter**
Send a letter to your child's school principal asking for an evaluation. You can say something like: "I am requesting a full evaluation for my child under IDEA to see if they qualify for special education services."

**Step 2: The School Responds**
The school has 10 days to respond to your request. They'll set up a meeting to discuss the evaluation.

**Step 3: Give Permission**
You'll sign a consent form allowing the school to evaluate your child. This is your right as a parent.

**Step 4: Evaluation Happens**
The school has 90 days to complete the evaluation. They'll look at your child's learning, behavior, and other areas.

**What Happens Next?**
After the evaluation, the school will meet with you to discuss if your child qualifies for an IEP.

**You're Not Alone**: If you need help with this process, the NC Autism Society can guide you: 1-800-442-2762.

Remember: You are your child's best advocate. Don't be afraid to ask questions."""
    },
    {
        "query": "What medications are covered for autism treatment?",
        "response": """I understand you're looking into medication options for your child. Here's what you should know:

**Important First Step**: Talk to your child's doctor before starting any medication. They know your child's specific needs.

**What Insurance Usually Covers**:
Most NC Medicaid and insurance plans cover medications that help with:
- Behavior challenges (like aggression or irritability)
- Anxiety or repetitive behaviors
- Sleep problems
- ADHD symptoms that happen with autism

**How to Find Out What's Covered**:
1. Call the number on the back of your insurance card
2. Ask about "autism-related medication coverage"
3. Ask if you need "prior authorization" (approval before getting the medication)

**What to Know About Medications**:
- There's no medication that "treats" autism itself
- Medications can help with specific challenges your child faces
- Therapy and behavioral support are still very important

**Need Help?**
- Your child's doctor can work with insurance for you
- NC Autism Society can help: 1-800-442-2762

You're doing a great job looking out for your child. Every child is different, so work closely with your doctor to find what's best for your family."""
    },
]


# Placeholder examples - You can add your actual prompt-response pairs here
PROVIDER_EXAMPLES_PLACEHOLDER: List[Example] = [
    {
        "query": "[Your example provider question here]",
        "response": "[Your ideal clinical response here]"
    },
    # Add 9 more examples as you collect them
]

PATIENT_EXAMPLES_PLACEHOLDER: List[Example] = [
    {
        "query": "[Your example parent/patient question here]",
        "response": "[Your ideal empathetic response here]"
    },
    # Add 9 more examples as you collect them
]


def get_examples(view_type: ViewType, use_placeholder: bool = False) -> List[Example]:
    """
    Get example query-response pairs for a specific view type.

    Args:
        view_type: Type of view - "provider" or "patient"
        use_placeholder: If True, returns placeholder examples for you to fill in

    Returns:
        List of example query-response pairs

    Raises:
        ValueError: If view_type is invalid

    Example:
        >>> examples = get_examples("provider")
        >>> # Returns PROVIDER_EXAMPLES
    """
    if use_placeholder:
        return PROVIDER_EXAMPLES_PLACEHOLDER if view_type == "provider" else PATIENT_EXAMPLES_PLACEHOLDER

    if view_type == "provider":
        return PROVIDER_EXAMPLES
    elif view_type == "patient":
        return PATIENT_EXAMPLES
    else:
        raise ValueError(f"Invalid view_type: {view_type}. Must be 'provider' or 'patient'")


def format_examples_for_prompt(examples: List[Example]) -> str:
    """
    Format examples into a string suitable for inclusion in LLM prompt.

    Args:
        examples: List of example query-response pairs

    Returns:
        Formatted string with examples

    Example:
        >>> examples = get_examples("provider")
        >>> formatted = format_examples_for_prompt(examples)
    """
    if not examples:
        return ""

    formatted_parts = []
    for i, example in enumerate(examples, 1):
        formatted_parts.append(f"""Example {i}:
Q: {example['query']}
A: {example['response']}
""")

    return "\n".join(formatted_parts)
