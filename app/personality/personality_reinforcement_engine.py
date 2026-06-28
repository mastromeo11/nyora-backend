from app.personality.personality_store import get_adaptive_personalities, append_personality
from app.personality.personality_models import AdaptivePersonalityNode

def reinforce_personality(
    personality_type: str,
    success: bool,
    latest_score: float = 1.0
) -> AdaptivePersonalityNode:
    """
    Applies reinforcement updates:
    - Success: confidence = 0.7 * old_confidence + 0.3 * latest_score
    - Failure: confidence *= 0.8
    """
    profiles = get_adaptive_personalities()
    node = None
    for p in profiles:
        if p.personality_type.lower() == personality_type.lower():
            node = p
            break

    if node is None:
        from app.personality.adaptive_personality_engine import get_or_create_personality
        node = get_or_create_personality(personality_type)

    node.reinforcement_count += 1
    
    if success:
        node.confidence = 0.7 * node.confidence + 0.3 * latest_score
    else:
        node.confidence *= 0.8

    node.confidence = min(max(node.confidence, 0.0), 1.0)
    append_personality(node)
    return node

