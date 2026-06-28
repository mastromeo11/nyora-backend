import uuid
from app.personality.personality_store import get_interaction_memories, append_interaction
from app.personality.personality_models import InteractionMemoryNode
from app.personality.privacy_filter_engine import filter_sensitive_info

def record_interaction(
    topic: str,
    task_type: str,
    success: bool
) -> InteractionMemoryNode:
    """
    Saves user interaction topic records. Enforces sensitive data firewall filtering.
    """
    clean_topic, _ = filter_sensitive_info(topic)
    clean_task, _ = filter_sensitive_info(task_type)

    mems = get_interaction_memories()
    node = None
    for m in mems:
        if m.topic.lower() == clean_topic.lower() and m.task_type.lower() == clean_task.lower():
            node = m
            break

    if node is None:
        node = InteractionMemoryNode(
            interaction_id=f"int_{uuid.uuid4().hex[:8]}",
            topic=clean_topic,
            task_type=clean_task,
            success_score=1.0 if success else 0.0,
            frequency=0,
            confidence=0.5
        )

    node.frequency += 1
    recent_score = 1.0 if success else 0.0
    node.success_score = 0.7 * node.success_score + 0.3 * recent_score
    node.confidence = min(node.confidence + 0.05, 1.0)

    append_interaction(node)
    
    # Trigger interaction compression if needed
    try:
        from app.personality.interaction_compression_engine import compress_interactions_if_needed
        compress_interactions_if_needed()
    except Exception as e:
        print(f"[INTERACTION ENGINE] Error running compression: {e}")

    return node
