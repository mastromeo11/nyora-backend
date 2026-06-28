from typing import List
from app.meta.meta_models import PolicyReplayNode, PlannerPolicyNode

_latest_explanation = ""

def get_latest_meta_explanation() -> str:
    global _latest_explanation
    return _latest_explanation

def compile_meta_explanation(replays: List[PolicyReplayNode], policies: List[PlannerPolicyNode]) -> str:
    """
    Compiles structured explanations for meta-cognitive choices without CoT leakage.
    Example:
    "Planner selected Vector Retrieval because similar policies achieved 94% success with lower latency."
    """
    global _latest_explanation
    if not replays:
        _latest_explanation = "Standard planner routing was selected based on default pipeline fallback."
        return _latest_explanation

    best_replay = replays[0]
    matched_policy = None
    for p in policies:
        if p.policy_id == best_replay.source_policy or p.signature == best_replay.target_policy:
            matched_policy = p
            break

    if matched_policy:
        success_pct = int(matched_policy.success_rate * 100)
        expl = (
            f"Planner selected {matched_policy.planner_type} because similar policies "
            f"achieved {success_pct}% success with lower latency."
        )
    else:
        expl = (
            f"Planner selected optimized routing path using replay "
            f"similarity of {best_replay.similarity * 100:.0f}% with past queries."
        )

    _latest_explanation = expl
    return expl
