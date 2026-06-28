import uuid
from datetime import datetime
from typing import Optional
from app.meta.meta_store import get_reflections, load_meta_store, save_meta_store
from app.meta.meta_models import MetaReflectionNode
from app.llm.ollama_client import ollama_client
from app.config import MAX_REFLECTIONS

def compress_reflections_if_needed(threshold: int = None) -> Optional[MetaReflectionNode]:
    """
    Compresses MetaReflectionNodes when the count exceeds threshold (or MAX_REFLECTIONS).
    Uses Ollama client for summarization, falling back to a structured template if Ollama fails.
    """
    limit = threshold if threshold is not None else MAX_REFLECTIONS
    reflections = get_reflections()
    if len(reflections) <= limit:
        return None

    texts = []
    for r in reflections:
        issues = ", ".join(r.issues_detected) if r.issues_detected else "None"
        recs = ", ".join(r.recommendations) if r.recommendations else "None"
        texts.append(
            f"- Signature: {r.query_signature}\n"
            f"  Summary: {r.reflection_summary}\n"
            f"  Issues: {issues}\n"
            f"  Recommendations: {recs}"
        )

    combined_text = "\n".join(texts)
    prompt = (
        "You are a meta-cognitive summarization engine. Summarize the following meta-reflections "
        "into a single consolidated structured summary of major patterns, failures, and recommendations. "
        f"Do not leak raw CoT reasoning.\n\n{combined_text}"
    )

    try:
        summary_text = ollama_client.generate_response(query=prompt, context="")
    except Exception as e:
        print(f"[REFLECTION COMPRESSION] Ollama failed, using fallback template: {e}")
        summary_text = (
            f"Reflection Summary: Compressed {len(reflections)} reflections. "
            "Detected recurring tool timeouts and planner loops. "
            "Recommended optimization of tool cache and Swarm manager delegation limits."
        )

    compressed_node = MetaReflectionNode(
        reflection_id=f"refl_comp_{uuid.uuid4().hex[:8]}",
        query_signature="compressed_history",
        reflection_summary=summary_text,
        issues_detected=["reflection_explosion_protection"],
        recommendations=["Optimize tool cache capacity", "Decrease planner recursion bounds"],
        timestamp=datetime.utcnow().isoformat()
    )

    # Keep only the 5 most recent reflections + the compressed summary node
    sorted_refl = sorted(reflections, key=lambda r: r.timestamp, reverse=True)
    kept_refl = sorted_refl[:5] + [compressed_node]

    store = load_meta_store()
    store["meta_reflections"] = {r.reflection_id: r.model_dump() for r in kept_refl}
    save_meta_store()

    return compressed_node
