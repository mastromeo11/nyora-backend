import uuid
from datetime import datetime
from app.meta.meta_store import (
    get_policies, append_archive, append_summary,
    load_meta_store, save_meta_store
)
from app.meta.meta_models import PolicyArchiveNode, PolicySummaryNode
from app.config import MAX_POLICY_HISTORY

def archive_old_policies_if_needed():
    """
    Checks if the count of PlannerPolicyNode nodes exceeds MAX_POLICY_HISTORY.
    If so, compresses the old policies into a PolicyArchiveNode,
    creates a matching PolicySummaryNode, and keeps only the 20 most recent policies.
    """
    policies = get_policies()
    if len(policies) <= MAX_POLICY_HISTORY:
        return None

    archive_id = f"arch_{uuid.uuid4().hex[:8]}"
    summary_id = f"sum_{uuid.uuid4().hex[:8]}"

    summaries_list = []
    tool_dists = {}
    successes = 0
    failures = 0
    conf_dists = {}
    latencies = []

    for p in policies:
        summaries_list.append(
            f"Policy {p.policy_id} ({p.planner_type}) - "
            f"Success: {p.success_rate:.2f}, Confidence: {p.confidence:.2f}"
        )
        if p.success_rate >= 0.5:
            successes += 1
        else:
            failures += 1
        conf_dists[p.policy_id] = p.confidence
        
        # Track tool distribution
        for t in getattr(p, "tool_sequence", []):
            tool_dists[t] = tool_dists.get(t, 0) + 1

        # Track latency score
        if getattr(p, "latency_score", None) is not None:
            latencies.append(p.latency_score)

    avg_success_rate = successes / len(policies) if policies else 1.0
    avg_confidence = sum(conf_dists.values()) / len(policies) if policies else 1.0

    latency_dists = {}
    if latencies:
        latency_dists = {
            "avg_latency_score": sum(latencies) / len(latencies),
            "min_latency_score": min(latencies),
            "max_latency_score": max(latencies)
        }

    # Create PolicyArchiveNode
    archive_node = PolicyArchiveNode(
        archive_id=archive_id,
        summary_id=summary_id,
        timestamp=datetime.utcnow().isoformat(),
        summaries=summaries_list,
        tool_distributions=tool_dists,
        success_metrics={
            "average_success_rate": avg_success_rate,
            "average_confidence": avg_confidence,
            "successes": float(successes),
            "failures": float(failures),
            "total_count": float(len(policies))
        },
        confidence_distributions=conf_dists,
        latency_distributions=latency_dists
    )
    append_archive(archive_node)

    # Create matching PolicySummaryNode
    summary_node = PolicySummaryNode(
        summary_id=summary_id,
        policy_ids=[p.policy_id for p in policies],
        summary=f"Archived {len(policies)} policy runs with average success rate {avg_success_rate:.2f}",
        successes=successes,
        failures=failures
    )
    append_summary(summary_node)

    # Prune policies from the store, keeping only the 20 most recent
    sorted_policies = sorted(policies, key=lambda p: p.recency, reverse=True)
    kept_policies = sorted_policies[:20]

    store = load_meta_store()
    store["planner_policies"] = {p.policy_id: p.model_dump() for p in kept_policies}
    save_meta_store()

    return archive_node
