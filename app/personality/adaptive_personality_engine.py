import uuid
from app.personality.personality_store import get_adaptive_personalities, append_personality
from app.personality.personality_models import AdaptivePersonalityNode

def get_or_create_personality(personality_type: str) -> AdaptivePersonalityNode:
    """
    Returns or instantiates a tone speak pattern configuration.
    Example types: teacher, concise engineer, researcher, mentor.
    """
    profiles = get_adaptive_personalities()
    for p in profiles:
        if p.personality_type.lower() == personality_type.lower():
            return p

    # Standard speaking configurations
    patterns = []
    prefs = []
    p_type = personality_type.lower()
    
    if "teacher" in p_type:
        patterns = ["Explain concepts thoroughly", "Use simple analogies", "Ask check questions"]
        prefs = ["Detailed answers", "No code dumps without explanations"]
    elif "engineer" in p_type or "concise" in p_type:
        patterns = ["Direct responses", "Code-first answers", "Minimal fluff"]
        prefs = ["Short verbosity", "Raw markdown code blocks"]
    elif "researcher" in p_type:
        patterns = ["Academic structure", "Provide citations for assertions", "High density details"]
        prefs = ["Detailed explanations", "Categorized evidence trees"]
    elif "mentor" in p_type:
        patterns = ["Encouraging statements", "Actionable advice", "Constructive feedback"]
        prefs = ["Medium verbosity", "Examples included"]
    else:
        patterns = ["Standard prompt routing speaking pattern"]
        prefs = ["Default explanations"]

    node = AdaptivePersonalityNode(
        personality_id=f"pers_{uuid.uuid4().hex[:8]}",
        personality_type=personality_type,
        speaking_patterns=patterns,
        explanation_preferences=prefs,
        confidence=0.5,
        reinforcement_count=0
    )
    append_personality(node)
    return node
