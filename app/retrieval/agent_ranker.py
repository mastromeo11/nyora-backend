from typing import List, Any
from app.config import OBSERVATION_WEIGHT, TASK_WEIGHT, MEMORY_WEIGHT_AGENT, EVIDENCE_WEIGHT

def _get_val(obj: Any, attr: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)
    try:
        if hasattr(obj, attr):
            return getattr(obj, attr, default)
    except Exception:
        pass
    return default

def rank_agent_traces(
    observations: List[Any],
    tasks: List[Any],
    memory_nodes: List[Any],
    evidence_nodes: List[Any]
) -> float:
    """
    Ranks agent traces using weighted scores:
    score = 0.30 * observation quality + 0.20 * task importance + 0.20 * memory overlap + 0.30 * evidence quality
    """
    # 1. Observation score (average confidence)
    obs_score = 0.0
    if observations:
        obs_score = sum([_get_val(o, "confidence", 0.8) for o in observations]) / len(observations)
    else:
        obs_score = 0.5  # Neutral default
        
    # 2. Task score (ratio of completed/successful tasks)
    task_score = 0.0
    if tasks:
        completed = sum([1 for t in tasks if str(_get_val(t, "status", "")).lower() == "completed"])
        task_score = completed / len(tasks)
    else:
        task_score = 1.0
        
    # 3. Memory overlap score (number of matched memory nodes, bounded)
    mem_score = min(len(memory_nodes) * 0.2, 1.0) if memory_nodes else 0.0
    
    # 4. Evidence quality (average retrieval score)
    ev_score = 0.0
    if evidence_nodes:
        ev_score = sum([_get_val(n, "retrieval_score", 0.5) for n in evidence_nodes]) / len(evidence_nodes)
    else:
        ev_score = 0.0
        
    # Apply weights
    final_score = (
        OBSERVATION_WEIGHT * obs_score +
        TASK_WEIGHT * task_score +
        MEMORY_WEIGHT_AGENT * mem_score +
        EVIDENCE_WEIGHT * ev_score
    )
    
    return round(final_score, 4)
