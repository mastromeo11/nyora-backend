import uuid
from app.personality.personality_store import (
    get_interaction_memories,
    get_recommendation_memories,
    append_interaction_summary,
    load_personality_store,
    save_personality_store
)
from app.personality.personality_models import InteractionSummaryNode

def compress_interactions_if_needed(threshold: int = 100) -> bool:
    """
    Checks interaction memory count. If it exceeds threshold, compresses
    them into an InteractionSummaryNode, and prunes active interactions.
    """
    mems = get_interaction_memories()
    if len(mems) <= threshold:
        return False

    topics = [m.topic for m in mems]
    tasks = [m.task_type for m in mems]
    
    # Extract accepted recommendations
    recs = get_recommendation_memories()
    accepted_items = [r.item for r in recs if r.accepted]

    summary_text = (
        f"Consolidated summary of {len(mems)} historical turns. "
        f"Primary focus domains include: {', '.join(set(topics[:5]))}. "
        f"Major tasks completed successfully: {', '.join(set(tasks[:5]))}."
    )

    node = InteractionSummaryNode(
        summary_id=f"int_sum_{uuid.uuid4().hex[:8]}",
        summary_text=summary_text,
        major_topics=list(set(topics)),
        successful_domains=list(set(topics)),
        response_patterns=list(set(tasks)),
        accepted_recommendations=list(set(accepted_items))
    )

    append_interaction_summary(node)

    # Prune interactions to keep the 5 most recent
    kept_mems = mems[-5:]
    store = load_personality_store()
    store["interaction_memories"] = {m.interaction_id: m.model_dump() for m in kept_mems}
    save_personality_store()

    return True
