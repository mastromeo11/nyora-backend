import uuid
from datetime import datetime
from app.meta.meta_store import get_optimization_failures, append_optimization_failure
from app.meta.meta_models import OptimizationFailureNode

def record_optimization_failure(query: str, failure_reason: str) -> OptimizationFailureNode:
    """
    Logs or increments an optimization failure signature.
    """
    failures = get_optimization_failures()
    node = None
    for f in failures:
        if f.query.lower() == query.lower() and f.failure_reason == failure_reason:
            node = f
            break

    if node is None:
        node = OptimizationFailureNode(
            failure_id=f"opt_fail_{uuid.uuid4().hex[:8]}",
            query=query,
            failure_reason=failure_reason,
            frequency=0,
            last_seen=datetime.utcnow().isoformat()
        )

    node.frequency += 1
    node.last_seen = datetime.utcnow().isoformat()

    append_optimization_failure(node)
    return node
