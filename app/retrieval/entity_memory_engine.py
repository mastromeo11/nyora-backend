from datetime import datetime
from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.retrieval.evidence_graph import get_node_entities
from app.retrieval.session_memory import get_session

def update_entity_memories(session_id: str, query: str, answer: str, sources: list, supporting_modalities: list, confidence_score: float):
    """
    Extracts entities from the current turn and updates their metadata in the entity memory cache.
    """
    session_data = get_session_cache(session_id)
    entity_memories = session_data.setdefault("entity_memories", {})
    turns = get_session(session_id)
    current_turn = len(turns)  # Current turn index
    
    # Extract entities mentioned in query or answer
    entities = get_node_entities(query).union(get_node_entities(answer))
    timestamp = datetime.utcnow().isoformat()
    
    for ent in entities:
        ent_key = ent.lower()
        mem = entity_memories.setdefault(ent_key, {
            "entity_name": ent_key,
            "mentions": 0,
            "last_seen": timestamp,
            "last_seen_turn": current_turn,
            "sources": [],
            "supporting_modalities": [],
            "confidence": 0.0
        })
        
        mem["mentions"] += 1
        mem["last_seen"] = timestamp
        mem["last_seen_turn"] = current_turn
        
        # Merge sources
        existing_srcs = set(mem.get("sources", []))
        for src in sources:
            existing_srcs.add(src)
        mem["sources"] = sorted(list(existing_srcs))
        
        # Merge supporting modalities
        existing_mods = set(mem.get("supporting_modalities", []))
        for mod in supporting_modalities:
            existing_mods.add(mod)
        mem["supporting_modalities"] = sorted(list(existing_mods))
        
        # Update confidence (running average or max)
        old_conf = mem.get("confidence", 0.0)
        # Average confidence
        mem["confidence"] = round((old_conf * (mem["mentions"] - 1) + confidence_score) / mem["mentions"], 4)
        
    save_session_cache(session_id, session_data)
