import uuid
from datetime import datetime
from app.meta.meta_store import get_reflection_failures, append_reflection_failure
from app.meta.meta_models import ReflectionFailureNode

def record_reflection_failure(reflection_id: str, failure_type: str) -> ReflectionFailureNode:
    """
    Logs reflection failure events in isolation.
    """
    failures = get_reflection_failures()
    node = None
    for f in failures:
        if f.reflection_id == reflection_id and f.failure_type == failure_type:
            node = f
            break

    if node is None:
        node = ReflectionFailureNode(
            failure_id=f"rf_{uuid.uuid4().hex[:8]}",
            reflection_id=reflection_id,
            failure_type=failure_type,
            frequency=0,
            last_seen=datetime.utcnow().isoformat()
        )

    node.frequency += 1
    node.last_seen = datetime.utcnow().isoformat()

    append_reflection_failure(node)
    return node
