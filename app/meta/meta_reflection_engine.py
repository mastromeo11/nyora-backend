import uuid
import hashlib
from datetime import datetime
from app.meta.meta_store import append_reflection
from app.meta.meta_models import MetaReflectionNode
from app.llm.ollama_client import ollama_client

def generate_meta_reflection(
    query: str,
    success: bool,
    tool_sequence: list,
    latency_ms: float,
    plan_steps: int,
    evidence_count: int
) -> MetaReflectionNode:
    """
    Evaluates the pipeline run for performance and safety issues.
    Constructs a MetaReflectionNode containing only a structured summary.
    """
    issues = []
    recs = []

    if evidence_count > 5:
        issues.append("excessive_retrieval")
        recs.append("Increase text/visual minimum scores to filter irrelevant evidence.")

    if len(tool_sequence) > 4:
        issues.append("excessive_simulation")
        recs.append("Increase tool cache hits to prevent duplicate execution.")

    if latency_ms > 2000.0:
        issues.append("slow_tools")
        recs.append("Optimize tool execution speed or employ semantic caches.")

    if plan_steps > 4:
        issues.append("planner_depth_overflow")
        recs.append("Set lower step limits inside ReAct planning loops.")

    query_sig = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]

    issues_str = ", ".join(issues) if issues else "None"
    recs_str = ", ".join(recs) if recs else "None"

    prompt = (
        "Construct a concise, structured post-execution summary for RAG query processing. "
        f"Query signature: {query_sig}. Success: {success}. Tools: {tool_sequence}. "
        f"Issues: {issues_str}. Recommendations: {recs_str}. "
        "Strictly write only the final evaluation summary without any thoughts or scratchpad."
    )

    try:
        summary_text = ollama_client.generate_response(query=prompt, context="")
    except Exception as e:
        print(f"[META REFLECTION] Ollama failed, using fallback template: {e}")
        status = "succeeded" if success else "failed"
        summary_text = (
            f"Query evaluation {status}. Latency: {latency_ms:.1f}ms. "
            f"Detected issues: {issues_str or 'None'}. "
            f"Recommendations: {recs_str or 'Maintain current parameters'}"
        )

    node = MetaReflectionNode(
        reflection_id=f"refl_{uuid.uuid4().hex[:8]}",
        query_signature=query_sig,
        reflection_summary=summary_text.strip(),
        issues_detected=issues,
        recommendations=recs,
        timestamp=datetime.utcnow().isoformat()
    )

    append_reflection(node)

    # Trigger automatic reflection compression checks
    try:
        from app.meta.reflection_compression_engine import compress_reflections_if_needed
        compress_reflections_if_needed(threshold=100)
    except Exception as err:
        print(f"[META REFLECTION] Error triggering reflection compression: {err}")

    return node
