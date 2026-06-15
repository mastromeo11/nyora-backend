import uuid
from datetime import datetime
from typing import List, Set, Dict, Any, Optional
from app.learning.learning_models import PatternNode
from app.learning.learning_store import get_patterns, append_pattern
from app.learning.query_signature_engine import generate_query_signature
from app.config import MIN_PATTERN_CONFIDENCE

def compile_and_store_pattern(
    query: str,
    entity_set: Set[str],
    intent_type: str,
    success: bool = True,
    evidence_ids: List[str] = None,
    source_modalities: List[str] = None
) -> PatternNode:
    """
    Compiles a new PatternNode or reinforces an existing query pattern.
    Uses query signature hashing to prevent duplicate patterns.
    """
    now_str = datetime.utcnow().isoformat()
    evidence_ids = evidence_ids or []
    source_modalities = source_modalities or []
    supporting_entities = list(entity_set)
    
    # 1. Generate signature hash
    sig = generate_query_signature(query, entity_set, intent_type)
    
    # 2. Check for existing pattern with same signature
    existing_patterns = get_patterns()
    matched_pattern: Optional[PatternNode] = None
    for pat in existing_patterns:
        if pat.signature == sig:
            matched_pattern = pat
            break

    if matched_pattern:
        # Reinforce existing pattern statistics
        freq = matched_pattern.frequency + 1
        succ = matched_pattern.success_count + (1 if success else 0)
        conf_count = matched_pattern.confirmation_count + 1
        
        # Calculate dynamic score components
        success_rate = succ / freq
        recency = 1.0  # Just reinforced now
        evidence_support = min(len(list(set(matched_pattern.evidence_ids + evidence_ids))) / 5.0, 1.0)
        freq_score = min(freq / 10.0, 1.0)
        
        # Compute pattern confidence:
        # 0.4 * frequency_score + 0.3 * success_rate + 0.2 * recency + 0.1 * evidence_support
        confidence = 0.4 * freq_score + 0.3 * success_rate + 0.2 * recency + 0.1 * evidence_support
        confidence = round(max(0.0, min(confidence, 1.0)), 4)
        
        updated_node = PatternNode(
            pattern_id=matched_pattern.pattern_id,
            signature=sig,
            frequency=freq,
            success_count=succ,
            confidence=confidence,
            importance_score=round(freq_score * success_rate, 4),
            supporting_entities=list(set(matched_pattern.supporting_entities + supporting_entities)),
            evidence_ids=list(set(matched_pattern.evidence_ids + evidence_ids)),
            source_modalities=list(set(matched_pattern.source_modalities + source_modalities)),
            last_confirmed=now_str,
            confirmation_count=conf_count,
            created_at=matched_pattern.created_at
        )
    else:
        # Create new pattern node
        freq = 1
        succ = 1 if success else 0
        success_rate = float(succ)
        recency = 1.0
        evidence_support = min(len(evidence_ids) / 5.0, 1.0)
        freq_score = 0.1
        
        confidence = 0.4 * freq_score + 0.3 * success_rate + 0.2 * recency + 0.1 * evidence_support
        confidence = round(max(0.0, min(confidence, 1.0)), 4)
        
        updated_node = PatternNode(
            pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
            signature=sig,
            frequency=freq,
            success_count=succ,
            confidence=confidence,
            importance_score=round(freq_score * success_rate, 4),
            supporting_entities=supporting_entities,
            evidence_ids=evidence_ids,
            source_modalities=source_modalities,
            last_confirmed=now_str,
            confirmation_count=1,
            created_at=now_str
        )
        
    append_pattern(updated_node)
    return updated_node
