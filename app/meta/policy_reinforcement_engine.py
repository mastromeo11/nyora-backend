from app.meta.meta_store import get_policies, append_policy
from app.meta.meta_models import PlannerPolicyNode
from app.meta.policy_reinforcement_statistics import update_policy_statistics

def reinforce_policy(
    policy_id: str,
    success: bool,
    outcome_score: float = 1.0,
    planner_type: str = "ReAct",
    signature: str = "",
    latency_ms: float = 0.0,
    tool_sequence: list = None
) -> PlannerPolicyNode:
    """
    Applies reinforcement updates to planner policy node confidence and success counts
    using statistics and a variance-penalized confidence score.
    """
    policies = get_policies()
    policy_node = None
    for p in policies:
        if p.policy_id == policy_id:
            policy_node = p
            break

    if policy_node is None:
        policy_node = PlannerPolicyNode(
            policy_id=policy_id,
            planner_type=planner_type,
            success_rate=1.0 if success else 0.0,
            confidence=0.5,
            importance=0.5,
            frequency=0,
            latency_score=1.0,
            recency=1.0,
            signature=signature or policy_id,
            tool_sequence=tool_sequence or []
        )

    if tool_sequence:
        policy_node.tool_sequence = tool_sequence

    # Capture historical values before update
    historical_confidence = policy_node.confidence
    historical_success = policy_node.success_rate

    # Update counts, averages, variance
    update_policy_statistics(policy_node, success, latency_ms, outcome_score)

    # Recalculate success rate
    policy_node.success_rate = policy_node.success_count / policy_node.frequency

    # Calculate variance penalty: 1 - abs(historical_success - recent_success)
    recent_success = 1.0 if success else 0.0
    variance_penalty = 1.0 - abs(historical_success - recent_success)

    # Calculate new confidence: 0.4 * historical + 0.3 * recent + 0.2 * variance_penalty + 0.1 * recency
    recent_outcome = outcome_score if success else 0.0
    recency = policy_node.recency if policy_node.recency is not None else 1.0

    new_confidence = 0.4 * historical_confidence + 0.3 * recent_outcome + 0.2 * variance_penalty + 0.1 * recency
    policy_node.confidence = min(max(new_confidence, 0.0), 1.0)

    append_policy(policy_node)
    return policy_node

