_latest_personality_explanation = ""

def get_latest_personality_explanation() -> str:
    global _latest_personality_explanation
    return _latest_personality_explanation

def compile_personality_explanation(
    preference_applied: bool,
    personality_type: str,
    reason_code: str = "success"
) -> str:
    """
    Compiles structured personalization explanations.
    Examples:
    "Concise formatting was selected because previous interactions indicated higher success with shorter explanations."
    "Academic research tone was selected to match the complex domain profile preferences."
    """
    global _latest_personality_explanation
    if not preference_applied:
        expl = "Standard formatting style was applied based on default pipeline fallback parameters."
    else:
        if personality_type.lower() == "teacher":
            expl = "Detailed explanation formatting was selected because previous interactions indicated higher success with thorough educational walkthroughs."
        elif personality_type.lower() == "concise engineer":
            expl = "Concise formatting was selected because previous interactions indicated higher success with shorter explanations."
        elif personality_type.lower() == "researcher":
            expl = "Academic research tone was selected to match the complex domain profile preferences."
        elif personality_type.lower() == "mentor":
            expl = "Encouraging explanation style was selected to match user preference learning profiles."
        else:
            expl = f"Personalized presentation configuration '{personality_type}' was active based on historical interaction success."
            
    _latest_personality_explanation = expl
    return expl
