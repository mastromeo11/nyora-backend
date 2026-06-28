import uuid
from typing import List
from app.meta.meta_store import get_policies, append_summary
from app.meta.meta_models import PolicySummaryNode
from app.llm.ollama_client import ollama_client

def compress_policies_into_summary(policy_ids: List[str]) -> PolicySummaryNode:
    """
    Compresses policy node execution paths into a single PolicySummaryNode.
    Queries the LLM or falls back to a formatted template summary if the LLM call fails.
    """
    policies = get_policies()
    matched = [p for p in policies if p.policy_id in policy_ids]
    if not matched:
        matched = policies

    planners = list(set([p.planner_type for p in matched]))
    latencies = [p.latency_score for p in matched]
    avg_latency = sum(latencies) / len(latencies) if latencies else 1.0
    avg_latency_s = max(0.1, (1.0 / avg_latency - 1.0))

    success_rates = [p.success_rate for p in matched]
    avg_success = sum(success_rates) / len(success_rates) if success_rates else 1.0

    successes = sum([1 for p in matched if p.success_rate >= 0.5])
    failures = len(matched) - successes

    prompt = (
        "Generate a structured, meta-cognitive summary for the following planner policy runs. "
        f"Planners: {planners}. Total policies: {len(matched)}. "
        f"Average success: {avg_success * 100:.1f}%. Avg Latency: {avg_latency_s:.1f}s. "
        f"Successes: {successes}. Failures: {failures}. "
        "Strictly return only the consolidation overview text without thoughts."
    )

    try:
        summary_text = ollama_client.generate_response(query=prompt, context="")
    except Exception as e:
        print(f"[POLICY COMPRESSION] Ollama error, applying template fallback: {e}")
        # Template summary format:
        # Planner=ReAct | Tools=[KG, Chroma] | Success=92% | Average latency=1.7s | Failures=2
        summary_text = (
            f"Planner={planners[0] if planners else 'ReAct'} | "
            "Tools=[KG, Chroma] | "
            f"Success={avg_success * 100:.0f}% | "
            f"Average latency={avg_latency_s:.1f}s | "
            f"Failures={failures}"
        )

    node = PolicySummaryNode(
        summary_id=f"sum_{uuid.uuid4().hex[:8]}",
        policy_ids=[p.policy_id for p in matched],
        summary=summary_text.strip(),
        successes=successes,
        failures=failures
    )

    append_summary(node)
    return node
