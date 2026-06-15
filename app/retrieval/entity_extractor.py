from datetime import datetime
from typing import List, Dict, Any, Set
from app.retrieval.entity_alias_registry import get_canonical_entities, normalize_entity_name
from app.retrieval.knowledge_models import EntityNode

def extract_entities_from_text(text: str) -> Set[str]:
    """
    Extracts canonical entity names from raw text string.
    """
    return get_canonical_entities(text)

def build_or_update_entity_node(
    existing_node: EntityNode = None,
    name: str = "",
    entity_type: str = "conceptual",
    source: str = None,
    modality: str = None,
    confidence: float = 1.0
) -> EntityNode:
    """
    Creates a new EntityNode or updates an existing one using incremental metrics.
    """
    now_str = datetime.utcnow().isoformat()
    canonical = normalize_entity_name(name)
    
    # Defaults
    aliases = [name] if name.lower() != canonical else []
    sources = [source] if source else []
    supporting_modalities = [modality] if modality else []
    mentions = 1
    created_at = now_str
    
    if existing_node:
        created_at = existing_node.created_at
        mentions = existing_node.mentions + 1
        
        # Merge lists
        aliases = list(set(existing_node.aliases + [name]))
        sources = list(set(existing_node.sources + ([source] if source else [])))
        supporting_modalities = list(set(existing_node.supporting_modalities + ([modality] if modality else [])))
        
    # Calculate components for entity_confidence
    # evidence_support = min(len(sources) / 5.0, 1.0)
    # modality_consensus = min(len(supporting_modalities) / 3.0, 1.0)
    # mention_frequency = min(mentions / 10.0, 1.0)
    # recency = 1.0 (since it is updated right now)
    
    evidence_support = min(len(sources) / 5.0, 1.0) if sources else 0.0
    modality_consensus = min(len(supporting_modalities) / 3.0, 1.0) if supporting_modalities else 0.0
    mention_frequency = min(mentions / 10.0, 1.0)
    recency = 1.0
    
    entity_confidence = (
        0.4 * evidence_support +
        0.3 * modality_consensus +
        0.2 * mention_frequency +
        0.1 * recency
    )
    # Clamp to [0.0, 1.0] range
    entity_confidence = round(max(0.0, min(entity_confidence, 1.0)), 4)
    
    return EntityNode(
        entity_id=f"entity_{canonical}",
        name=name,
        canonical_name=canonical,
        entity_type=entity_type,
        aliases=aliases,
        mentions=mentions,
        confidence=entity_confidence,
        sources=sources,
        supporting_modalities=supporting_modalities,
        created_at=created_at,
        updated_at=now_str,
        last_seen=now_str
    )
