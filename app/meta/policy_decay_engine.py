from app.meta.meta_store import load_meta_store, save_meta_store
from app.config import POLICY_DECAY_FACTOR, TOOL_DECAY_FACTOR

def decay_meta_memory():
    """
    Applies fractional decays over time:
    - confidence *= 0.99 (POLICY_DECAY_FACTOR)
    - importance *= 0.98 (TOOL_DECAY_FACTOR)
    - success_rate *= 0.995
    """
    store = load_meta_store()

    # Decay planner policies
    policies = store.setdefault("planner_policies", {})
    for p_id, p in policies.items():
        p["confidence"] = max(0.0, p.get("confidence", 1.0) * POLICY_DECAY_FACTOR)
        p["success_rate"] = max(0.0, p.get("success_rate", 1.0) * 0.995)
        p["importance"] = max(0.0, p.get("importance", 1.0) * TOOL_DECAY_FACTOR)

    # Decay tool learnings
    tools = store.setdefault("tool_learnings", {})
    for t_id, t in tools.items():
        t["confidence"] = max(0.0, t.get("confidence", 1.0) * POLICY_DECAY_FACTOR)
        t["success_rate"] = max(0.0, t.get("success_rate", 1.0) * 0.995)
        t["importance_score"] = max(0.0, t.get("importance_score", 1.0) * TOOL_DECAY_FACTOR)

    save_meta_store()
