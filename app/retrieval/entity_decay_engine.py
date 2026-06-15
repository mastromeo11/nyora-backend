from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.retrieval.session_memory import get_session

def compute_entity_scores(session_id: str) -> dict:
    """
    Computes decayed scores for all entities tracked in session's memory.
    active_entity_score = mention_count * (0.9 ** (current_turn - last_seen_turn))
    """
    session_data = get_session_cache(session_id)
    entity_memories = session_data.get("entity_memories", {})
    turns = get_session(session_id)
    current_turn = len(turns)
    
    decayed_scores = {}
    for ent, memory in entity_memories.items():
        # entity memories store fields: mentions, last_seen_turn
        mentions = memory.get("mentions", 0)
        last_seen_turn = memory.get("last_seen_turn", 0)
        
        # Calculate score using formula
        turns_since_seen = max(0, current_turn - last_seen_turn)
        score = mentions * (0.9 ** turns_since_seen)
        decayed_scores[ent] = round(score, 4)
        
    return decayed_scores

def get_top_active_entities(session_id: str, limit: int = 5) -> list:
    """
    Returns sorted list of entity names based on decayed scores.
    """
    scores = compute_entity_scores(session_id)
    sorted_ents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [ent for ent, score in sorted_ents[:limit]]
