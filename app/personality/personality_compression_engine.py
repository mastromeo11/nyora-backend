import uuid
from typing import List, Optional
from app.personality.personality_store import get_preferences, append_personality_summary, load_personality_store, save_personality_store
from app.personality.personality_models import PersonalitySummaryNode
from app.llm.ollama_client import ollama_client

def compress_preferences_into_summary(threshold: int = 100) -> Optional[PersonalitySummaryNode]:
    """
    Consolidates historical user preferences into a structured summary.
    Invokes Ollama or falls back to template consolidation upon LLM timeout.
    """
    prefs = get_preferences()
    if len(prefs) <= threshold:
        return None

    pref_texts = []
    major_prefs = []
    styles = []
    
    for p in prefs:
        major_prefs.append(p.explanation_depth)
        styles.append(p.tone_preference)
        pref_texts.append(
            f"- Preferred Depth: {p.explanation_depth}, Tone: {p.tone_preference}, Response Length: {p.response_length}"
        )

    combined_text = "\n".join(pref_texts)
    prompt = (
        "Consolidate the following historical user interaction preference nodes into a concise "
        "personality summary profiling major habits, formatting needs, and tone styles.\n\n"
        f"{combined_text}\n\n"
        "Strictly output only the consolidated summary sentence without thoughts."
    )

    try:
        summary_text = ollama_client.generate_response(query=prompt, context="")
    except Exception as e:
        print(f"[PERSONALITY COMPRESSION] Ollama failed, using fallback template: {e}")
        # Default template fallback
        major_pref_set = set(major_prefs)
        style_set = set(styles)
        summary_text = (
            f"User prefers {', '.join(major_pref_set) if major_pref_set else 'medium'} depth "
            f"with a {', '.join(style_set) if style_set else 'professional'} tone style."
        )

    node = PersonalitySummaryNode(
        summary_id=f"pers_sum_{uuid.uuid4().hex[:8]}",
        summary_text=summary_text.strip(),
        major_preferences=list(set(major_prefs)),
        styles=list(set(styles)),
        habits=["Adaptive prompt routing", "Explanation preference preservation"]
    )
    append_personality_summary(node)

    # Prune preferences, keeping only the 5 most recent
    sorted_prefs = sorted(prefs, key=lambda p: p.timestamp, reverse=True)
    kept_prefs = sorted_prefs[:5]

    store = load_personality_store()
    store["preferences"] = {p.preference_id: p.model_dump() for p in kept_prefs}
    save_personality_store()

    return node
