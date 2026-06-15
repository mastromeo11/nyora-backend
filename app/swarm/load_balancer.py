from typing import List, Dict, Any
from app.swarm.agent_monitor import get_agent_health

def get_agent_score(agent_id: str) -> float:
    health_data = get_agent_health(agent_id)
    health = health_data["health_score"]
    
    success_count = health_data["success_count"]
    failure_count = health_data["failure_count"]
    total = success_count + failure_count
    success_rate = (success_count / total) if total > 0 else 1.0
    
    avg_latency = health_data["average_latency"]
    latency_score = max(0.0, 1.0 - (avg_latency / 2000.0))
    
    agent_score = 0.4 * health + 0.3 * latency_score + 0.3 * success_rate
    return round(max(0.0, min(agent_score, 1.0)), 4)

def select_best_agent(agent_candidates: List[str]) -> str:
    if not agent_candidates:
        raise ValueError("[LOAD BALANCER] Candidates list is empty.")
        
    scored = [(get_agent_score(cand), cand) for cand in agent_candidates]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]
