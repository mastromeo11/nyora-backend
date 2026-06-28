from app.meta.meta_models import PlannerPolicyNode

def update_policy_statistics(
    node: PlannerPolicyNode,
    success: bool,
    latency_ms: float,
    confidence_val: float
):
    """
    Updates PlannerPolicyNode statistics: frequency, success/failure counts,
    average latency, and confidence variance using recent history.
    """
    # 1. Update frequency and success/failure counts
    if success:
        node.success_count = getattr(node, "success_count", 0) + 1
    else:
        node.failure_count = getattr(node, "failure_count", 0) + 1

    # Frequency matches total runs
    total_runs = node.success_count + node.failure_count
    node.frequency = total_runs

    # 2. Update average latency
    current_avg = getattr(node, "average_latency", 0.0)
    node.average_latency = (current_avg * (total_runs - 1) + latency_ms) / total_runs

    # 3. Track confidence history and calculate variance
    history = getattr(node, "confidence_history", None)
    if history is None:
        history = []
    history.append(confidence_val)
    node.confidence_history = history

    if len(history) > 1:
        mean = sum(history) / len(history)
        variance = sum((c - mean) ** 2 for c in history) / len(history)
        node.confidence_variance = variance
    else:
        node.confidence_variance = 0.0
