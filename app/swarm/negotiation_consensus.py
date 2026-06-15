import uuid
from datetime import datetime
from typing import Dict, List, Any
from app.swarm.agent_store import append_consensus
from app.swarm.agent_cache import consensus_cache, record_hit, record_miss

def calculate_consensus_score(
    confidence: float,
    grounding_score: float,
    agreement: float,
    evidence_quality: float,
    recency: float
) -> float:
    score = (
        0.30 * confidence +
        0.25 * grounding_score +
        0.20 * agreement +
        0.15 * evidence_quality +
        0.10 * recency
    )
    return round(max(0.0, min(score, 1.0)), 4)

def resolve_agent_consensus(
    topic: str,
    proposals: List[Dict[str, Any]],
    critic_feedback: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Evaluates Proposals from disputing agents and forms a unified consensus node.
    """
    cache_key = f"consensus_{topic}_{len(proposals)}"
    cached = consensus_cache.get(cache_key)
    if cached is not None:
        record_hit()
        return cached
        
    record_miss()
    
    critic_feedback = critic_feedback or {}
    has_critic_contradiction = critic_feedback.get("contradiction_detected", False)
    
    now_str = datetime.utcnow().isoformat()
    agreed_fact = ""
    agreement_ratio = 1.0
    
    if not proposals:
        agreed_fact = "No proposals offered."
        score = 0.0
    else:
        votes = {}
        for prop in proposals:
            val = prop.get("proposal", "").strip()
            weight = prop.get("weight", 1.0)
            votes[val] = votes.get(val, 0.0) + weight
            
        sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        agreed_fact = sorted_votes[0][0]
        
        total_votes = sum(votes.values())
        agreement_ratio = (sorted_votes[0][1] / total_votes) if total_votes > 0 else 1.0
        
        if has_critic_contradiction:
            agreement_ratio = max(0.1, agreement_ratio - 0.4)
            
        confidence = proposals[0].get("confidence", 0.8)
        grounding_score = 0.9 if not has_critic_contradiction else 0.5
        evidence_quality = 0.8
        recency = 1.0
        
        score = calculate_consensus_score(confidence, grounding_score, agreement_ratio, evidence_quality, recency)
        
    consensus_id = f"con_{uuid.uuid4().hex[:8]}"
    node = {
        "consensus_id": consensus_id,
        "topic": topic,
        "agreed_fact": agreed_fact,
        "consensus_score": score,
        "agreement_ratio": agreement_ratio,
        "timestamp": now_str
    }
    
    consensus_cache.set(cache_key, node)
    append_consensus(node)
    
    return node
