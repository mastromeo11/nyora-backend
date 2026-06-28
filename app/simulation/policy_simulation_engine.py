import uuid
from datetime import datetime
from typing import List, Optional
from app.simulation.simulation_models import PolicyNode
from app.simulation.simulation_store import append_policy, get_policies

def record_policy_execution(
    policy_id: str,
    actions: List[str],
    success: bool,
    confidence: float,
    latency_ms: float,
    importance: float = 0.5
) -> PolicyNode:
    """
    Records a policy execution, recalculates scores, latency, and reinforcements.
    """
    existing_policies = get_policies()
    match = None
    for p in existing_policies:
        if p.policy_id == policy_id:
            match = p
            break
            
    now_str = datetime.utcnow().isoformat()
    
    if match:
        match.frequency += 1
        if success:
            match.success_count += 1
            match.last_success = now_str
        match.success_rate = match.success_count / match.frequency
        match.confidence = 0.7 * match.confidence + 0.3 * confidence
        match.average_latency = 0.7 * match.average_latency + 0.3 * latency_ms
        match.average_confidence = 0.7 * match.average_confidence + 0.3 * confidence
        match.last_used = now_str
        match.reinforcement_score += confidence
        policy_node = match
    else:
        policy_node = PolicyNode(
            policy_id=policy_id,
            actions=actions,
            success_rate=1.0 if success else 0.0,
            confidence=confidence,
            frequency=1,
            success_count=1 if success else 0,
            last_used=now_str,
            last_success=now_str if success else None,
            average_latency=latency_ms,
            average_confidence=confidence,
            reinforcement_score=confidence
        )
        
    append_policy(policy_node)
    return policy_node

def calculate_policy_score(policy: PolicyNode, importance_val: float = 0.5) -> float:
    """
    Computes a composite policy score using:
        0.3 * success_rate + 0.25 * confidence + 0.2 * importance + 0.15 * recency + 0.1 * latency_score
    """
    success_rate = policy.success_rate
    confidence = policy.confidence
    
    # Recency: based on last_used timestamp compared to now
    try:
        time_diff = (datetime.utcnow() - datetime.fromisoformat(policy.last_used)).total_seconds()
        recency = max(0.0, 1.0 - (time_diff / 86400.0))  # Decays over 24 hours
    except Exception:
        recency = 1.0
        
    # Latency: lower latency is better, normalize so that 0ms is 1.0, 10000ms is 0.0
    latency_score = max(0.0, 1.0 - (policy.average_latency / 10000.0))
    
    score = (0.3 * success_rate + 
             0.25 * confidence + 
             0.2 * importance_val + 
             0.15 * recency + 
             0.1 * latency_score)
             
    return max(0.0, min(1.0, score))
