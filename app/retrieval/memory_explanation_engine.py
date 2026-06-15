from app.retrieval.followup_resolver import get_latest_followup_debug
from app.retrieval.memory_cache import get_session_cache

# Thread-safe global store for the latest memory explanation diagnostic
_latest_memory_explanation = {
    "resolved_query": "",
    "resolution_method": "none",
    "active_entity": None,
    "memory_sources": []
}

def get_latest_memory_explanation() -> dict:
    """
    Returns the latest computed memory explanation diagnostic.
    """
    return _latest_memory_explanation

def compile_memory_diagnostics(session_id: str, original_query: str, resolved_query: str) -> dict:
    """
    Compiles memory usage explanations, indicating active entity, resolved query,
    resolution method, and which memory components influenced the result.
    """
    global _latest_memory_explanation
    
    debug_followup = get_latest_followup_debug()
    session_data = get_session_cache(session_id)
    
    current_focus = session_data.get("current_entity_focus", "")
    
    # Determine the resolution method
    stage = debug_followup.get("stage", "none")
    
    # Determine memory sources used
    memory_sources = []
    if "Stage 1" in stage:
        memory_sources.append("active_entity_focus")
    elif "Stage 2" in stage:
        memory_sources.append("recent_turns")
    elif "Stage 3" in stage:
        memory_sources.append("session_summary")
    elif "Stage 4" in stage:
        memory_sources.append("ollama_phi3")
        
    diag = {
        "resolved_query": resolved_query,
        "resolution_method": stage,
        "active_entity": current_focus.upper() if current_focus else None,
        "memory_sources": memory_sources
    }
    
    _latest_memory_explanation = diag
    return diag
