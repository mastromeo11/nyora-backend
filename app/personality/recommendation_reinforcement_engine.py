import uuid
from app.personality.personality_store import get_recommendation_memories, append_recommendation
from app.personality.personality_models import RecommendationMemoryNode
from app.personality.recommendation_signature_engine import generate_recommendation_signature

def reinforce_recommendation(
    item: str,
    category: str,
    accepted: bool,
    latest_score: float = 1.0
) -> RecommendationMemoryNode:
    """
    Applies reinforcement updating to recommendation score:
    - Accepted: confidence = 0.7 * old_confidence + 0.3 * latest_score
    - Rejected: confidence *= 0.8
    """
    sig = generate_recommendation_signature(item, category, "recommend")
    recs = get_recommendation_memories()
    node = None
    for r in recs:
        if getattr(r, "signature", None) == sig:
            node = r
            break
        elif r.item.lower() == item.lower() and r.category.lower() == category.lower():
            node = r
            break

    if node is None:
        node = RecommendationMemoryNode(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            item=item,
            category=category,
            accepted=accepted,
            rejected=not accepted,
            confidence=0.5,
            frequency=0,
            signature=sig
        )

    node.frequency += 1
    node.signature = sig
    
    if accepted:
        node.accepted = True
        node.confidence = 0.7 * node.confidence + 0.3 * latest_score
    else:
        node.rejected = True
        node.confidence *= 0.8

    append_recommendation(node)
    return node
