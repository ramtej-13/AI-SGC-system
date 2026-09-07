import re
from typing import Tuple

# Transparent, Rule-Based Severity & Safety Keywords
# NOTE: This is an explicit rule-based heuristic engine (NOT Machine Learning),
# guaranteeing auditability, predictability, and safety compliance for campus operations.

HIGH_PRIORITY_PATTERNS = [
    (r"\b(spark|sparking|fire|smoke|shock|electrocution|short circuit|live wire)\b", "Electrical Safety Hazard"),
    (r"\b(burst|flooding|flood|gas leak|cylinder leak|suffocating)\b", "Physical Safety & Hazard"),
    (r"\b(stuck in elevator|lift stuck|trapped|door jammed)\b", "Entrapment Emergency"),
    (r"\b(poisoning|vomiting|contaminated|food poisoning|dead insect|stray dog)\b", "Health & Hygiene Emergency"),
    (r"\b(fell|falling plaster|ceiling collapsed|sharp nail|exposed nail|bleeding|injury)\b", "Structural & Bodily Hazard"),
    (r"\b(emergency|urgent|asap|critical|immediate danger)\b", "Urgent Student Flag")
]

MEDIUM_PRIORITY_PATTERNS = [
    (r"\b(leak|leaking|dripping|overflow|clogged|choked)\b", "Plumbing & Drainage Issue"),
    (r"\b(flicker|flickering|power cut|outage|breaker|mcb|tripped)\b", "Power Supply Disruption"),
    (r"\b(down|unreachable|offline|500 error|cannot connect|wifi down|internet down|portal down)\b", "IT / Connectivity Disruption"),
    (r"\b(broken|damaged|not working|stopped running|defective|jammed)\b", "Equipment Malfunction"),
    (r"\b(dirty|smell|foul|stinking|garbage|overflowing bin|unhygienic)\b", "Cleanliness & Sanitation Concern"),
    (r"\b(exam|hall ticket|admit card|internal marks|attendance shortage|revaluation)\b", "Academic Examination Constraint")
]

def calculate_priority(text: str, category: str = "") -> Tuple[str, str]:
    """
    Evaluates grievance text using rule-based pattern matching to determine priority
    (High, Medium, Low) along with transparent rationale.
    
    Returns:
        (priority: str, reason: str)
    """
    if not text:
        return ("Low", "Default baseline priority for minimal text")

    text_lower = text.lower()

    # 1. Check High Priority Safety / Emergency Rules
    for pattern, reason in HIGH_PRIORITY_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return ("High", f"Critical: Triggered by keyword '{match.group(0)}' ({reason})")

    # 2. Check Medium Priority Functional Impact Rules
    for pattern, reason in MEDIUM_PRIORITY_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return ("Medium", f"Operational: Triggered by keyword '{match.group(0)}' ({reason})")

    # 3. Category-specific baseline rules
    if category in ["Electrical", "Plumbing", "Laboratory"]:
        return ("Medium", f"Department standard SLA baseline for {category}")

    # 4. Default to Low Priority
    return ("Low", "Standard non-emergency grievance routine SLA")
