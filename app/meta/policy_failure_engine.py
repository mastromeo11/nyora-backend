import uuid
from datetime import datetime
from app.meta.meta_store import get_policy_failures, append_policy_failure
from app.meta.meta_models import PolicyFailureNode
from app.meta.policy_reinforcement_engine import reinforce_policy

def record_policy_failure(policy_id: str, failure_reason: str) -> PolicyFailureNode:
    """
    Records a planner policy failure (loops, bad routing, timeouts, etc.)
    and applies a confidence penalty.
    """
    failures = get_policy_failures()
    node = None
    for f in failures:
        if f.policy_id == policy_id and f.failure_reason == failure_reason:
            node = f
            break

    if node is None:
        node = PolicyFailureNode(
            failure_id=f"pf_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            failure_reason=failure_reason,
            frequency=0,
            last_seen=datetime.utcnow().isoformat()
        )

    node.frequency += 1
    node.last_seen = datetime.utcnow().isoformat()

    append_policy_failure(node)

    # Penalize the policy confidence in the planner engine
    try:
        reinforce_policy(policy_id, success=False)
    except Exception as e:
        print(f"[POLICY FAILURE ENGINE] Error applying failure penalty: {e}")

    return node
