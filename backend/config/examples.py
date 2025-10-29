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
        "response": """**Eligibility Criteria**:
1. IDD diagnosis documented by qualified professional
2. Age ≥3 years
3. ICF/IID level of care via CAP-DA assessment
4. NC residency with legal immigration status
5. Medicaid-eligible or meets Medicaid financial criteria

**Application Process**:
- Contact LME/MCO (Alliance: 1-800-510-9132 | Vaya: 1-800-849-6127 | Partners: 1-888-235-4673 | Trillium: 1-877-685-2415)
- Complete CAP-DA assessment
- Slot assignment from waitlist (priority based on population status)"""
    },
    {
        "query": "How do I refer a patient for IEP evaluation?",
        "response": """**Referral Process**:
1. Submit written referral to school principal or Director of Exceptional Children
2. Include educational concerns and supporting documentation
3. Request comprehensive psychoeducational evaluation under IDEA

**Timeline**:
- School response: 10 business days
- Evaluation completion: 90 days from parental consent

**Evaluation Domains** (as indicated):
Cognitive functioning, academic achievement, communication, motor skills, behavioral/emotional functioning, adaptive behavior

**Clinical Documentation**: Medical records, developmental history, diagnostic reports

**Regulatory Requirements**: Prior written notice and parental consent required (34 CFR §300.304)

**Resource**: NC DPI Exceptional Children Division: 919-807-3969"""
    },
    {
        "query": "What medications are covered for autism treatment?",
        "response": """**NC Medicaid Coverage** (requires FDA approval for indication + medical necessity):
- Atypical antipsychotics (risperidone, aripiprazole): irritability/aggression
- SSRIs: co-morbid anxiety/OCD
- Stimulants/atomoxetine: co-morbid ADHD
- Sleep medications: documented sleep disorders

**Prior Authorization**: Required for certain medications. Submit clinical documentation.

**Clinical Considerations**:
- No FDA-approved medications for core autism symptoms
- Pharmacotherapy targets behavioral/psychiatric co-morbidities only
- Evidence-based behavioral interventions = first-line treatment

**Recommendations**: Review patient formulary and PA requirements. Consider referral to developmental-behavioral pediatrician or child psychiatrist."""
    },
]


# ============================================================================
# Patient/Parent Examples (Empathetic, Plain Language Tone)
# ============================================================================

PATIENT_EXAMPLES: List[Example] = [
    {
        "query": "I need help for my child with autism but I'm not sure where to start.",
        "response": """In North Carolina, each county is served by a Local Management Entity/Managed Care Organization (LME/MCO) that manages Medicaid services for mental health, developmental disabilities and substance-use needs. They can connect you to programs like the Innovations Waiver and 1915(i) services, which offer home- and community-based supports, respite and crisis services. To find your LME/MCO, use the state directory or call 1-855-262-1946. You do not need to know the program names in advance—describe your child's needs, and the LME/MCO will explain the options and help you apply.

Would you like help finding the phone number for your county's LME/MCO or learning how to apply for Medicaid if you aren't already enrolled?"""
    },
    {
        "query": "We need support at home for daily activities—what programs could help us?",
        "response": """Two main Medicaid programs provide in-home support: the Innovations Waiver and 1915(i) services. Both are designed for people with intellectual or developmental disabilities. The Innovations Waiver offers assistance with daily tasks like bathing, dressing and cooking; support for community participation; and adaptations to your home or vehicle. 1915(i) services (which replaced an earlier program called 1915(b)(3)) help children and adults learn skills to live at home and participate in the community, find a job and provide respite for caregivers. Your LME/MCO can tell you which program fits your situation and help you join the Innovations waitlist or apply for 1915(i) services.

Are you currently enrolled in Medicaid, or would you like guidance on how to get coverage so you can access these services?"""
    },
    {
        "query": "My child is having a behavioral crisis. Is there someone who can come to us?",
        "response": """Yes. North Carolina has mobile crisis teams—counselors who can meet you at home, school or another safe place to help calm the situation. Mobile crisis services are available 24 hours a day, seven days a week and are free even if you don't have insurance. They will listen, assess the situation and connect you with ongoing support. For immediate danger, call 988 or 911 and ask for a Crisis Intervention Team officer. Otherwise, you can call your LME/MCO's crisis line to reach a mobile crisis team.

Is anyone in immediate danger? If not, would you like the phone number for your local mobile crisis provider?"""
    },
    {
        "query": "We're overwhelmed and need a break—are there programs that support caregivers?",
        "response": """Both the Innovations Waiver and 1915(i) services include respite care and other caregiver supports. The Innovations Waiver provides scheduled breaks and emergency respite, as well as training and consultations to help family and friends support you better. 1915(i) services can also give caregivers a break and teach skills to help your loved one live more independently. To access respite, contact your LME/MCO and explain that you need caregiver support; they will help determine which program you qualify for.

Do you want information on joining the Innovations waitlist or applying for 1915(i) services to start getting respite support?"""
    },
    {
        "query": "I've heard there are services to help adults with disabilities live on their own. How does that work?",
        "response": """1915(i) services are designed to help adults and children with mental-health conditions, substance-use disorders, traumatic brain injuries or intellectual/developmental disabilities live and work in their communities. They can teach skills to live at home, participate in the community and find employment. They also provide respite and community transition support. These services are available through Medicaid Tailored Plans, NC Medicaid Direct or the Eastern Band of Cherokee Indians Tribal Option. An LME/MCO care manager will help you set goals and coordinate services.

Do you know which Medicaid plan you have? If not, would you like help finding out so we can determine whether you can access 1915(i) services?"""
    },
    {
        "query": "Our therapist mentioned 'Intensive In-Home.' What does that mean?",
        "response": """Intensive In-Home (IIH) services are team-based mental-health supports for children and young adults (ages 3–20) who are experiencing severe behavioral or emotional challenges. A team of therapists and case managers works with the whole family in your home to provide individual therapy, family therapy, crisis intervention, behavioral interventions, and coaching on daily routines and coping skills. IIH is intended to prevent out-of-home placements and is covered by Medicaid and some private insurance plans. Eligibility usually requires that outpatient therapy has been tried and that the child's needs are intense.

Have you already tried outpatient therapy, and would you like help contacting your LME/MCO to see if your child qualifies for Intensive In-Home services?"""
    },
    {
        "query": "I'm not sure what Medicaid plan I have or what services I'm eligible for.",
        "response": """NC Medicaid offers different plan types. Standard Plans cover general physical and behavioral health, while Tailored Plans provide additional services for people with serious mental illness, substance-use disorders, or I/DD. 1915(i) services are only available with Tailored Plans, NC Medicaid Direct or the Eastern Band of Cherokee Indians Tribal Option and are not available through Standard Plans. If you're unsure which plan you have, call the NC Medicaid Enrollment Broker at 1-833-870-5500. You can also call your LME/MCO or look at your Medicaid ID card.

Would you like me to help you identify your plan or provide instructions on how to call the enrollment broker?"""
    },
    {
        "query": "I have Medicaid but don't know who to call for help with mental-health or developmental-disability services.",
        "response": """Start with your LME/MCO. They manage mental-health, I/DD and substance-use services for Medicaid beneficiaries in your county. The LME/MCO directory lists phone numbers and crisis lines. Alliance Health (1-800-510-9132), Partners Health Management (1-888-235-4673), Trillium Health Resources (1-877-685-2415) and Vaya Health (1-800-962-9003) are the four LME/MCOs. If you don't know which serves your county, call 1-855-262-1946 for assistance.

Would you like me to look up which LME/MCO serves your county and provide the contact number?"""
    },
    {
        "query": "Is there a program that helps pay for ramps or other modifications to my home or vehicle?",
        "response": """Yes. The Innovations Waiver covers home and vehicle modifications to make your environment safer and more accessible. It also pays for assistive technologies like communication devices and smart-home tools. To access these supports, you need to have a waiver slot. If you aren't yet on the waiver, contact your LME/MCO to join the waitlist. While waiting, some equipment may be covered through other Medicaid programs, so ask your care manager.

Are you already on the Innovations waitlist, or would you like guidance on how to apply and explore interim options while you wait?"""
    },
    {
        "query": "We're struggling to get to appointments. Is transportation available?",
        "response": """NC Medicaid offers Non-Emergency Medical Transportation (NEMT), which provides free rides to and from doctor visits, mental-health appointments, and pharmacies. You should request a ride at least two days before your appointment. If you drive yourself or are driven by a friend or family member, you may be reimbursed for travel costs. To schedule a ride, call the NEMT number on your Medicaid card or contact your health plan.

Do you need assistance finding the phone number to schedule NEMT or learning about mileage reimbursement?"""
    },
]


def get_examples(view_type: ViewType) -> List[Example]:
    """
    Get example query-response pairs for a specific view type.

    Args:
        view_type: Type of view - "provider" or "patient"

    Returns:
        List of example query-response pairs

    Raises:
        ValueError: If view_type is invalid

    Example:
        >>> examples = get_examples("provider")
        >>> # Returns PROVIDER_EXAMPLES
    """
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
