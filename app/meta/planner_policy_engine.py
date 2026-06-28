import uuid
from datetime import datetime
from app.meta.meta_store import get_policies, append_policy
from app.meta.meta_models import PlannerPolicyNode
from app.meta.policy_signature_engine import generate_policy_signature
from app.meta.policy_reinforcement_engine import reinforce_policy

def record_policy_run(
    policy_id: str,
    planner_type: str,
    tool_sequence: list,
    intent_type: str,
    entities: list,
    success: bool,
    latency_ms: float,
    confidence: float = 1.0,
    importance: float = 1.0
) -> PlannerPolicyNode:
    """
    Records a planner policy run. Determines the deterministic signature,
    and applies reinforcement engine updates.
    """
    sig = generate_policy_signature(planner_type, tool_sequence, intent_type, entities)
    
    # Reinforce policy
    node = reinforce_policy(
        policy_id=policy_id,
        success=success,
        outcome_score=confidence,
        planner_type=planner_type,
        signature=sig,
        latency_ms=latency_ms,
        tool_sequence=tool_sequence
    )

    # Recalculate latency score and recency
    node.latency_score = 1.0 / (1.0 + latency_ms / 1000.0)
    node.recency = 1.0
    node.importance = importance

    append_policy(node)
    
    # Run automatic compression check
    try:
        from app.meta.policy_archive_engine import archive_old_policies_if_needed
        archive_old_policies_if_needed()
    except Exception as e:
        print(f"[PLANNER POLICY ENGINE] Archive compression trigger error: {e}")

    return node

def get_policy_score(node: PlannerPolicyNode) -> float:
    """
    Calculates dynamic score of a planner policy using the Milestone 16 weights.
    policy_score = 0.30 * success_rate + 0.25 * confidence + 0.20 * importance + 0.15 * recency + 0.10 * latency_score
    """
    score = (
        0.30 * node.success_rate +
        0.25 * node.confidence +
        0.20 * node.importance +
        0.15 * node.recency +
        0.10 * node.latency_score
    )
    return min(max(score, 0.0), 1.0)
