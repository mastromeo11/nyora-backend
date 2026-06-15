from datetime import datetime
from app.retrieval.memory_cache import get_session_cache, save_session_cache

def update_preferences_from_query(session_id: str, query: str):
    """
    Parses the user query for formatting, style, language, or model preferences.
    Updates the session's preference cache.
    """
    q_lower = query.lower()
    session_data = get_session_cache(session_id)
    prefs = session_data.setdefault("preference_memory", {})
    
    timestamp = datetime.utcnow().isoformat()
    
    # 1. Parse Language
    languages = {
        "english": "English",
        "french": "French",
        "spanish": "Spanish",
        "german": "German",
        "italian": "Italian"
    }
    for kw, lang in languages.items():
        if f"in {kw}" in q_lower or f"translate to {kw}" in q_lower:
            prefs["preferred_language"] = val = lang
            
    # 2. Parse Style / Length
    if "short" in q_lower or "brief" in q_lower or "concise" in q_lower:
        prefs["preferred_style"] = "brief"
    elif "detailed" in q_lower or "explain in detail" in q_lower or "verbose" in q_lower:
        prefs["preferred_style"] = "detailed"
        
    # 3. Parse preferred model references
    if "phi3" in q_lower or "phi-3" in q_lower:
        prefs["preferred_model"] = "phi3:mini"
    elif "llama3" in q_lower or "llama 3" in q_lower:
        prefs["preferred_model"] = "llama3.1"
        
    # 4. Parse Domain focus
    if "multimodal" in q_lower:
        prefs["preferred_domain"] = "multimodal rag"
    elif "text only" in q_lower or "plain text" in q_lower:
        prefs["preferred_domain"] = "text rag"
        
    if prefs:
        session_data["preference_memory"] = prefs
        save_session_cache(session_id, session_data)
