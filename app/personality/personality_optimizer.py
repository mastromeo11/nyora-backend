from app.personality.personality_store import get_adaptive_personalities
from app.personality.personality_replay_engine import get_personality_replays_ranked
from app.personality.adaptive_personality_engine import get_or_create_personality

def select_adaptive_personality(query: str) -> str:
    """
    Selects the optimal personality type (concise engineer, researcher, teacher, mentor)
    based on query content, similar replays, and confidence metrics.
    """
    # 1. Similarity replay match
    replays = get_personality_replays_ranked(query)
    if replays and replays[0].similarity_score >= 0.6:
        return replays[0].source_personality

    # 2. Heuristics based on query keywords
    q = query.lower()
    if "concise" in q or "short" in q or "brief" in q or "code-first" in q:
        return "concise engineer"
    if "explain" in q or "why" in q or "analogy" in q or "teach" in q:
        return "teacher"
    if "citation" in q or "paper" in q or "academic" in q or "research" in q:
        return "researcher"
    if "guidance" in q or "help" in q or "mentor" in q:
        return "mentor"

    # 3. Choose the profile with the highest confidence
    profiles = get_adaptive_personalities()
    if profiles:
        best_profile = max(profiles, key=lambda p: p.confidence)
        if best_profile.confidence >= 0.5:
            return best_profile.personality_type

    return "concise engineer"  # Default fallback

