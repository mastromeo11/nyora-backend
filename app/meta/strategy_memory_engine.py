import uuid
from typing import List, Optional
from app.meta.meta_store import get_strategies, append_strategy
from app.meta.meta_models import StrategyNode
from app.embedding.text_embedder import embed_text

def record_strategy_routing(
    query_pattern: str,
    planner_id: str,
    tool_ids: List[str],
    success: bool,
    confidence: float = 1.0,
    intent: str = "",
    entities: List[str] = []
) -> StrategyNode:
    """
    Stores or updates successful routing strategy patterns (query -> planner -> tools -> outcome).
    """
    from app.meta.strategy_signature_engine import generate_strategy_signature
    sig = generate_strategy_signature(intent, planner_id, tool_ids, entities)

    strategies = get_strategies()
    node = None
    for s in strategies:
        if getattr(s, "signature", None) == sig:
            node = s
            break
        elif s.query_pattern.lower() == query_pattern.lower() and s.planner_id == planner_id:
            node = s
            break

    if node is None:
        node = StrategyNode(
            strategy_id=f"strat_{uuid.uuid4().hex[:8]}",
            query_pattern=query_pattern,
            planner_id=planner_id,
            tool_ids=tool_ids,
            success_rate=1.0 if success else 0.0,
            confidence=confidence,
            signature=sig
        )
    else:
        node.signature = sig

    # Accumulate fields
    frequency = getattr(node, "frequency", 0) + 1
    node.frequency = frequency

    if success:
        node.success_rate = (node.success_rate * (frequency - 1) + 1.0) / frequency
        node.confidence = 0.7 * node.confidence + 0.3 * confidence
    else:
        node.success_rate = (node.success_rate * (frequency - 1) + 0.0) / frequency
        node.confidence *= 0.8

    append_strategy(node)
    return node

def match_similar_strategy(query: str) -> Optional[StrategyNode]:
    """
    Finds the strategy with highest cosine similarity or text overlap to the query.
    Returns the strategy if the similarity score is above 0.4.
    """
    strategies = get_strategies()
    if not strategies:
        return None

    best_strategy = None
    best_sim = -1.0

    try:
        q_emb = embed_text([query])[0]
        patterns = [s.query_pattern for s in strategies]
        p_embs = embed_text(patterns)

        for idx, s in enumerate(strategies):
            p_emb = p_embs[idx]
            dot_prod = sum(a * b for a, b in zip(q_emb, p_emb))
            mag_q = sum(a * a for a in q_emb) ** 0.5
            mag_p = sum(b * b for b in p_emb) ** 0.5
            sim = dot_prod / (mag_q * mag_p + 1e-9)

            # Direct overlap boost
            if s.query_pattern.lower() in query.lower() or query.lower() in s.query_pattern.lower():
                sim += 0.2

            if sim > best_sim:
                best_sim = sim
                best_strategy = s
    except Exception as e:
        print(f"[STRATEGY MEMORY ENGINE] Embedding similarity error, falling back to word overlap: {e}")
        for s in strategies:
            q_words = set(query.lower().split())
            p_words = set(s.query_pattern.lower().split())
            overlap = len(q_words & p_words)
            sim = overlap / max(len(q_words), 1)
            if sim > best_sim:
                best_sim = sim
                best_strategy = s

    if best_strategy and best_sim >= 0.4:
        return best_strategy
    return None
