import uuid
from datetime import datetime
from typing import List, Any
from app.simulation.simulation_models import HypothesisNode
from app.simulation.simulation_store import append_hypothesis, get_hypotheses

def generate_hypothesis(
    description: str,
    supporting_entities: List[str] = None,
    evidence_score: float = 1.0,
    memory_score: float = 1.0,
    recurrence_score: float = 1.0,
    recency_score: float = 1.0,
    supporting_episode_ids: List[str] = None,
    supporting_pattern_ids: List[str] = None,
    supporting_evidence_ids: List[str] = None
) -> HypothesisNode:
    """
    Creates or updates a HypothesisNode.
    Confidence score formula:
        0.4 * evidence_score + 0.3 * memory_score + 0.2 * recurrence_score + 0.1 * recency_score
    """
    supporting_entities = supporting_entities or []
    supporting_episode_ids = supporting_episode_ids or []
    supporting_pattern_ids = supporting_pattern_ids or []
    supporting_evidence_ids = supporting_evidence_ids or []
    
    # Check if a hypothesis with same description exists
    existing = get_hypotheses()
    match = None
    for h in existing:
        if h.description.strip().lower() == description.strip().lower():
            match = h
            break
            
    now_str = datetime.utcnow().isoformat()
    confidence = 0.4 * evidence_score + 0.3 * memory_score + 0.2 * recurrence_score + 0.1 * recency_score
    confidence = max(0.0, min(1.0, confidence))
    
    if match:
        match.confirmation_count += 1
        match.last_confirmed = now_str
        match.confidence = 0.7 * match.confidence + 0.3 * confidence
        match.supporting_entities = list(set(match.supporting_entities + supporting_entities))
        match.supporting_episode_ids = list(set(match.supporting_episode_ids + supporting_episode_ids))
        match.supporting_pattern_ids = list(set(match.supporting_pattern_ids + supporting_pattern_ids))
        match.supporting_evidence_ids = list(set(match.supporting_evidence_ids + supporting_evidence_ids))
        node_to_save = match
    else:
        node_to_save = HypothesisNode(
            hypothesis_id=f"hyp_{uuid.uuid4().hex[:8]}",
            description=description,
            supporting_entities=supporting_entities,
            supporting_evidence=supporting_evidence_ids,
            confidence=confidence,
            created_at=now_str,
            last_confirmed=now_str,
            confirmation_count=1,
            supporting_episode_ids=supporting_episode_ids,
            supporting_pattern_ids=supporting_pattern_ids,
            supporting_evidence_ids=supporting_evidence_ids
        )
        
    append_hypothesis(node_to_save)
    return node_to_save
