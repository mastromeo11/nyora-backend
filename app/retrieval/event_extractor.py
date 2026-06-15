import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.retrieval.entity_alias_registry import get_canonical_entities
from app.retrieval.knowledge_models import TemporalNode

def extract_events_from_text(
    text: str,
    event_type: str = "conversation_evolution",
    timestamp_override: str = None
) -> List[TemporalNode]:
    """
    Parses conversational text or execution logs to detect chronological milestones.
    Returns a list of TemporalNode objects.
    """
    events = []
    text_lower = text.lower()
    entities = list(get_canonical_entities(text))
    
    # Event triggers
    triggers = [
        ("select", "component_selection"),
        ("choose", "component_selection"),
        ("add", "component_addition"),
        ("connect", "component_wiring"),
        ("discuss", "topic_discussion"),
        ("create", "object_creation")
    ]
    
    matched_type = event_type
    matched_desc = ""
    
    for word, etype in triggers:
        if word in text_lower:
            matched_type = etype
            # Crop a small snippet around trigger
            idx = text_lower.find(word)
            start = max(0, idx - 20)
            end = min(len(text), idx + 40)
            matched_desc = text[start:end].strip() + "..."
            break
            
    if not matched_desc:
        if len(text) > 50:
            matched_desc = text[:47] + "..."
        else:
            matched_desc = text
            
    now_str = timestamp_override or datetime.utcnow().isoformat()
    
    if entities:
        event = TemporalNode(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            description=matched_desc,
            timestamp=now_str,
            entities=entities,
            event_type=matched_type,
            created_at=now_str,
            updated_at=now_str,
            last_seen=now_str
        )
        events.append(event)
        
    return events
