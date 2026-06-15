import re
from app.retrieval.memory_cache import get_session_cache
from app.retrieval.session_memory import get_recent_turns
from app.llm.ollama_client import ollama_client

ENTITY_DISPLAY_NAMES = {
    "chromadb": "ChromaDB",
    "fastapi": "FastAPI",
    "ollama": "Ollama",
    "clip": "CLIP",
    "whisper": "Whisper"
}

# Thread-safe global store for pronoun resolution debug logs
_latest_followup_debug = {
    "original_query": "",
    "resolved_query": "",
    "stage": "",
    "focus_used": ""
}

def get_latest_followup_debug() -> dict:
    return _latest_followup_debug

def _replace_pronouns(query: str, display_name: str) -> str:
    """
    Utility to replace pronouns with a specific display name.
    """
    # Replace possessive "its" -> "Display's"
    q_resolved = re.sub(r"\bits\b", f"{display_name}'s", query, flags=re.IGNORECASE)
    # Replace other pronouns -> "Display"
    q_resolved = re.sub(r"\b(it|they|this|that|those|them)\b", display_name, q_resolved, flags=re.IGNORECASE)
    return q_resolved

def resolve_followup(query: str, session_id: str) -> str:
    """
    Hierarchically resolves pronouns in the query to produce a standalone query.
    """
    global _latest_followup_debug
    
    q_lower = query.lower()
    pronouns = ["it", "they", "this", "that", "its", "those", "them"]
    has_pronoun = any(re.search(rf"\b{p}\b", q_lower) for p in pronouns)
    has_ambiguity = has_pronoun or "earlier" in q_lower or "component" in q_lower or "database" in q_lower or "system" in q_lower
    
    # If no pronouns or ambiguity, return query as is
    if not has_ambiguity:
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": query,
            "stage": "none (no ambiguity)",
            "focus_used": ""
        }
        return query
        
    session_data = get_session_cache(session_id)
    current_focus = session_data.get("current_entity_focus")
    previous_focus = session_data.get("previous_entity_focus")
    
    # --- Stage 1: Fast Regex with Current / Previous Focus ---
    if current_focus and current_focus in ENTITY_DISPLAY_NAMES:
        display = ENTITY_DISPLAY_NAMES[current_focus]
        resolved = _replace_pronouns(query, display)
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": resolved,
            "stage": "Stage 1 (Current Focus)",
            "focus_used": display
        }
        return resolved
        
    if previous_focus and previous_focus in ENTITY_DISPLAY_NAMES:
        display = ENTITY_DISPLAY_NAMES[previous_focus]
        resolved = _replace_pronouns(query, display)
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": resolved,
            "stage": "Stage 1 (Previous Focus)",
            "focus_used": display
        }
        return resolved
        
    # --- Stage 2: Search Recent Turns (latest 2 turns) and Entity Memory ---
    recent_turns = get_recent_turns(session_id, 2)
    found_entity = None
    for turn in reversed(recent_turns):
        for ent in ENTITY_DISPLAY_NAMES.keys():
            # Check if entity was mentioned in previous queries or answers
            if ent in turn.user_query.lower() or ent in turn.assistant_answer.lower():
                found_entity = ent
                break
        if found_entity:
            break
            
    if found_entity:
        display = ENTITY_DISPLAY_NAMES[found_entity]
        resolved = _replace_pronouns(query, display)
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": resolved,
            "stage": "Stage 2 (Recent Turns)",
            "focus_used": display
        }
        return resolved
        
    # --- Stage 3: Search Summarized Memory ---
    summaries = session_data.get("summaries", [])
    if summaries:
        latest_summary = summaries[-1]  # dict or ConversationSummary
        summary_text = latest_summary.get("summary", "") if isinstance(latest_summary, dict) else getattr(latest_summary, "summary", "")
        # Scan summary for standard entities
        for ent in ENTITY_DISPLAY_NAMES.keys():
            if ent in summary_text.lower():
                found_entity = ent
                break
                
    if found_entity:
        display = ENTITY_DISPLAY_NAMES[found_entity]
        resolved = _replace_pronouns(query, display)
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": resolved,
            "stage": "Stage 3 (Summary Memory)",
            "focus_used": display
        }
        return resolved
        
    # --- Stage 4: Local LLM Fallback (Ollama phi3:mini) ---
    all_recent_turns = get_recent_turns(session_id, 5)
    if not all_recent_turns:
        # No history to resolve against, return original
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": query,
            "stage": "Stage 4 Fallback (No History)",
            "focus_used": ""
        }
        return query
        
    # Build history context for LLM
    history_lines = []
    for turn in all_recent_turns:
        history_lines.append(f"User: {turn.user_query}")
        history_lines.append(f"Assistant: {turn.assistant_answer}")
    history_text = "\n".join(history_lines)
    
    prompt = f"""You are an assistant that resolves pronouns and ambiguous references in user queries.
Given the conversation history and the final user query, rewrite the final query to make it a standalone, explicit question.
Do not explain, do not answer it, only output the rewritten question.

Examples:
History:
User: Which database is used?
Assistant: ChromaDB is used.
Final Query: Why was it selected?
Resolved Query: Why was ChromaDB selected?

History:
{history_text}

Final Query: {query}
Resolved Query:"""

    try:
        # LLM Generation
        raw_res = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
        # Clean response
        resolved = raw_res.strip().replace('"', '').replace("'", "")
        # Remove any leading/trailing "Resolved Query:" text
        resolved = re.sub(r"^resolved query:\s*", "", resolved, flags=re.IGNORECASE)
        
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": resolved,
            "stage": "Stage 4 (LLM Resolver)",
            "focus_used": "Ollama phi3:mini"
        }
        return resolved
    except Exception as e:
        print(f"Error invoking LLM resolver: {e}")
        _latest_followup_debug = {
            "original_query": query,
            "resolved_query": query,
            "stage": "Stage 4 Fallback (LLM Failure)",
            "focus_used": ""
        }
        return query
