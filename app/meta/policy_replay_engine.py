import uuid
from typing import List
from app.meta.meta_store import get_policies, get_replays, append_replay
from app.meta.meta_models import PolicyReplayNode
from app.meta.policy_similarity_cache import similarity_cache
from app.embedding.text_embedder import embed_text

def record_policy_replay(source_id: str, target_id: str, similarity: float, success: bool) -> PolicyReplayNode:
    """
    Appends or updates a PolicyReplayNode indicating matching and replaying.
    """
    replays = get_replays()
    node = None
    for r in replays:
        if r.source_policy == source_id and r.target_policy == target_id:
            node = r
            break

    if node is None:
        node = PolicyReplayNode(
            replay_id=f"rep_{uuid.uuid4().hex[:8]}",
            source_policy=source_id,
            target_policy=target_id,
            similarity=similarity,
            frequency=0,
            success_count=0
        )

    node.frequency += 1
    if success:
        node.success_count += 1

    append_replay(node)
    return node

def get_replays_ranked(query: str) -> List[PolicyReplayNode]:
    """
    Scores and ranks past planner policy replays:
    score = 0.25*similarity + 0.20*success + 0.20*confidence + 0.15*importance + 0.10*recency + 0.10*frequency
    Ensures successful policies outrank failed ones by applying penalties to failures.
    """
    policies = get_policies()
    if not policies:
        return []

    try:
        q_emb = embed_text([query])[0]
    except Exception:
        q_emb = [0.0] * 384

    scored_replays = []
    for p in policies:
        # Check cache
        cached_node = similarity_cache.get(query, p.policy_id)
        if cached_node is not None:
            similarity = cached_node.similarity
        else:
            try:
                p_emb = embed_text([p.signature])[0]
                dot_prod = sum(a * b for a, b in zip(q_emb, p_emb))
                mag_q = sum(a * a for a in q_emb) ** 0.5
                mag_p = sum(b * b for b in p_emb) ** 0.5
                similarity = dot_prod / (mag_q * mag_p + 1e-9)
            except Exception:
                similarity = 0.5
            similarity_cache.put(query, p.policy_id, similarity)

        freq_score = min(p.frequency / 10.0, 1.0)
        score = (
            0.25 * similarity +
            0.20 * p.success_rate +
            0.20 * p.confidence +
            0.15 * p.importance +
            0.10 * p.recency +
            0.10 * freq_score
        )

        # Successful policies must outrank failures
        if p.success_rate < 0.5:
            score -= 10.0  # Penalize failures heavily

        rep_node = PolicyReplayNode(
            replay_id=f"rep_{uuid.uuid4().hex[:8]}",
            source_policy=p.policy_id,
            target_policy=p.signature,
            similarity=similarity,
            frequency=p.frequency,
            success_count=int(p.success_rate * p.frequency)
        )
        scored_replays.append((score, rep_node))

    # Sort descending by score
    scored_replays.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_replays]
