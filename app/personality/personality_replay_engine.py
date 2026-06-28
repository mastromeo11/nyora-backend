import uuid
from typing import List
from app.personality.personality_store import get_adaptive_personalities, get_personality_replays, append_personality_replay
from app.personality.personality_models import PersonalityReplayNode
from app.personality.personality_similarity_cache import personality_similarity_cache
from app.embedding.text_embedder import embed_text

def record_personality_replay(
    source_personality: str,
    target_query: str,
    similarity_score: float
) -> PersonalityReplayNode:
    """
    Saves a replay signature mapping queries to adaptive style profiles.
    """
    node = PersonalityReplayNode(
        replay_id=f"pers_rep_{uuid.uuid4().hex[:8]}",
        source_personality=source_personality,
        target_query=target_query,
        similarity_score=similarity_score
    )
    append_personality_replay(node)
    return node

def get_personality_replays_ranked(query: str) -> List[PersonalityReplayNode]:
    """
    Calculates cosine similarities between query embeddings and speaking pattern signatures.
    Ranks replays by similarity, filtering out profiles with low confidence.
    """
    profiles = get_adaptive_personalities()
    if not profiles:
        return []

    try:
        q_emb = embed_text([query])[0]
    except Exception:
        q_emb = [0.0] * 384

    ranked_replays = []
    for p in profiles:
        # Check ordered pair cache
        cached_node = personality_similarity_cache.get(query, p.personality_id)
        if cached_node is not None:
            similarity = cached_node.similarity
        else:
            try:
                sig_text = " ".join(p.speaking_patterns)
                p_emb = embed_text([sig_text])[0]
                
                dot = sum(a * b for a, b in zip(q_emb, p_emb))
                mag_q = sum(a * a for a in q_emb) ** 0.5
                mag_p = sum(b * b for b in p_emb) ** 0.5
                similarity = dot / (mag_q * mag_p + 1e-9)
            except Exception:
                similarity = 0.5
            personality_similarity_cache.put(query, p.personality_id, similarity)

        score = 0.5 * similarity + 0.5 * p.confidence
        
        rep_node = PersonalityReplayNode(
            replay_id=f"rep_{uuid.uuid4().hex[:8]}",
            source_personality=p.personality_type,
            target_query=query,
            similarity_score=similarity
        )
        ranked_replays.append((score, rep_node))

    ranked_replays.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in ranked_replays]
