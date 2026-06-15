import uuid
from datetime import datetime
from app.retrieval.memory_models import MemoryNode
from app.retrieval.session_memory import get_session
from app.retrieval.memory_cache import get_session_cache
from app.retrieval.importance_engine import calculate_importance

def retrieve_memories(session_id: str) -> list:
    """
    Collects conversational context from short-term memory (turns),
    long-term memory (summaries), entity memories, and preference memories.
    Converts them to a list of MemoryNode objects.
    """
    memory_nodes = []
    
    turns = get_session(session_id)
    session_data = get_session_cache(session_id)
    summaries = session_data.get("summaries", [])
    entity_memories = session_data.get("entity_memories", {})
    prefs = session_data.get("preference_memory", {})
    
    # 1. Retrieve short-term memory (turns)
    for idx, turn in enumerate(turns):
        turn_id = getattr(turn, "turn_id", f"turn_{idx+1}")
        
        # Calculate dynamic importance score
        importance = calculate_importance(
            query=turn.user_query,
            answer=turn.assistant_answer,
            citations=turn.retrieved_sources,
            confidence_score=1.0 if turn.confidence.lower() == "high" else 0.5
        )
        
        content = f"Recent turn: User query: '{turn.user_query}' | Assistant answer: '{turn.assistant_answer}'."
        memory_nodes.append(MemoryNode(
            memory_id=f"mem_turn_{turn_id}",
            memory_type="turn_node",
            content=content,
            source=f"turn_{idx+1}",
            score=0.0,  # Will be ranked/scored in ranker
            timestamp=turn.timestamp,
            importance=importance
        ))
        
    # 2. Retrieve long-term memory (summaries)
    for idx, summ in enumerate(summaries):
        summary_text = summ.get("summary", "")
        important_facts = summ.get("important_facts", [])
        timestamp = summ.get("timestamp", datetime.utcnow().isoformat())
        content = f"Previous conversation summary: {summary_text}"
        if important_facts:
            facts_str = "; ".join(important_facts)
            content += f" | Important facts: {facts_str}"
            
        memory_nodes.append(MemoryNode(
            memory_id=f"mem_summary_{idx+1}",
            memory_type="summary_node",
            content=content,
            source=f"summary_{idx+1}",
            score=0.0,
            timestamp=timestamp,
            importance=0.8
        ))
        
    # 3. Retrieve Entity memory
    for ent, mem in entity_memories.items():
        mentions = mem.get("mentions", 0)
        sources = ", ".join(mem.get("sources", []))
        modalities = ", ".join(mem.get("supporting_modalities", []))
        last_seen = mem.get("last_seen", datetime.utcnow().isoformat())
        
        content = f"Entity '{ent}' mentions count={mentions}, last seen={last_seen}, sources={sources}, modalities={modalities}."
        memory_nodes.append(MemoryNode(
            memory_id=f"mem_entity_{ent}",
            memory_type="entity_node",
            content=content,
            source=f"entity_memory_{ent}",
            score=0.0,
            timestamp=last_seen,
            importance=0.7
        ))
        
    # 4. Retrieve Preference memory
    for key, val in prefs.items():
        content = f"User preference: {key} is {val}."
        memory_nodes.append(MemoryNode(
            memory_id=f"mem_pref_{key}",
            memory_type="preference_node",
            content=content,
            source=f"preference_memory_{key}",
            score=0.0,
            timestamp=datetime.utcnow().isoformat(),
            importance=0.9
        ))
        
    return memory_nodes
