from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.retrieval.evidence_graph import get_node_entities

ENTITY_TOPIC_NAMES = {
    "chromadb": "ChromaDB database integration",
    "fastapi": "FastAPI web application routing",
    "ollama": "Ollama local LLM reasoning",
    "clip": "CLIP visual semantic embedding",
    "whisper": "Whisper audio speech segments"
}

def track_active_entities(session_id: str, query: str, answer: str):
    """
    Updates the current and previous entity focus states along with conversation topic.
    """
    session_data = get_session_cache(session_id)
    
    current_focus = session_data.get("current_entity_focus")
    
    # Extract entities
    q_ents = get_node_entities(query)
    a_ents = get_node_entities(answer)
    
    new_focus = None
    if q_ents:
        # Prioritize query entities, sort alphabetically for determinism or pick the first
        new_focus = sorted(list(q_ents))[0]
    elif a_ents:
        # Fallback to answer entities
        new_focus = sorted(list(a_ents))[0]
        
    if new_focus:
        if new_focus != current_focus:
            session_data["previous_entity_focus"] = current_focus
            session_data["current_entity_focus"] = new_focus
            
            # Update active_entities list (keep a history of unique active entities)
            active_list = session_data.get("active_entities", [])
            if new_focus not in active_list:
                active_list.append(new_focus)
            session_data["active_entities"] = active_list
            
            # Update conversation topic
            topic = ENTITY_TOPIC_NAMES.get(new_focus, f"{new_focus.capitalize()} topic")
            session_data["conversation_topic"] = topic
            
    save_session_cache(session_id, session_data)
