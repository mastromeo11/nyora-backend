import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.retrieval.entity_alias_registry import get_canonical_entities, normalize_entity_name
from app.retrieval.knowledge_models import RelationNode
from app.config import MIN_RELATION_CONFIDENCE

# Standard patterns mapping keywords to relation types
RELATION_PATTERNS = [
    (["connects to", "connect directly to", "connects directly to", "connected to"], "CONNECTS_TO"),
    (["uses", "utilizes", "using", "work with"], "USES"),
    (["depends on", "dependency", "reliant on"], "DEPENDS_ON"),
    (["part of", "member of", "inside of"], "PART_OF"),
    (["generates", "provides", "creates", "produces", "generate"], "GENERATES"),
    (["selected for", "selected because", "chosen for"], "SELECTED_FOR"),
    (["surrounds", "surround", "surrounded by", "around"], "SURROUNDED_BY"),
    (["previously discussed", "discussed earlier"], "PREVIOUSLY_DISCUSSED"),
    (["derived from", "derive from", "extraction of"], "DERIVED_FROM"),
    (["observed", "observation of", "observed by"], "OBSERVED_BY"),
    (["discovered", "found in", "discovered in"], "DISCOVERED_IN"),
    (["related to", "associated with"], "RELATED_TO")
]

def extract_relations_from_text(
    text: str,
    evidence_ids: List[str] = None,
    source_modalities: List[str] = None,
    created_by: str = "relation_extractor"
) -> List[RelationNode]:
    """
    Scans text to detect semantic connections between co-occurring canonical entities.
    Returns a list of RelationNodes.
    """
    relations = []
    text_lower = text.lower()
    entities = list(get_canonical_entities(text))
    
    if len(entities) < 2:
        return relations
        
    now_str = datetime.utcnow().isoformat()
    evidence_ids = evidence_ids or []
    source_modalities = source_modalities or []
    
    # Process pair-wise combinations of co-occurring entities
    for i in range(len(entities)):
        for j in range(len(entities)):
            if i == j:
                continue
            ent_a = entities[i]
            ent_b = entities[j]
            
            # Look for specific relation keywords between them in the text
            for keywords, rel_type in RELATION_PATTERNS:
                matched = False
                for kw in keywords:
                    # Check if keyword occurs between the two entities, or generally in the text segment
                    if kw in text_lower:
                        # Ensure the order is correct or logical for directional relations
                        if rel_type in ["CONNECTS_TO", "USES", "DEPENDS_ON", "SELECTED_FOR", "GENERATES", "DERIVED_FROM"]:
                            idx_a = text_lower.find(ent_a)
                            idx_b = text_lower.find(ent_b)
                            idx_kw = text_lower.find(kw)
                            if idx_a != -1 and idx_b != -1 and idx_kw != -1:
                                if not (idx_a < idx_kw < idx_b):
                                    continue # Skip if order doesn't match entity A -> keyword -> entity B
                        
                        matched = True
                        break
                        
                if matched:
                    # Compute confidence
                    # relation_confidence = 0.5 * evidence_support + 0.3 * confirmations + 0.2 * recency
                    evidence_support = min(len(evidence_ids) / 5.0, 1.0) if evidence_ids else 0.2
                    confirmations = 1.0 # First confirmation
                    recency = 1.0
                    
                    rel_conf = 0.5 * evidence_support + 0.3 * confirmations + 0.2 * recency
                    rel_conf = round(max(0.0, min(rel_conf, 1.0)), 4)
                    
                    if rel_conf >= MIN_RELATION_CONFIDENCE:
                        rel = RelationNode(
                            relation_id=f"rel_{ent_a}_{rel_type.lower()}_{ent_b}",
                            source_entity=ent_a,
                            target_entity=ent_b,
                            relation_type=rel_type,
                            confidence=rel_conf,
                            weight=rel_conf,
                            created_at=now_str,
                            updated_at=now_str,
                            evidence_ids=evidence_ids,
                            source_modalities=source_modalities,
                            created_by=created_by,
                            last_confirmed=now_str,
                            confirmation_count=1
                        )
                        relations.append(rel)
                        break # Only extract one relation type per entity pair per text segment
                        
    return relations
