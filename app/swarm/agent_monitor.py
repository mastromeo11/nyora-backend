import threading
from datetime import datetime
from typing import Dict, Any

_monitor_lock = threading.Lock()
_metrics: Dict[str, Dict[str, Any]] = {}

def record_agent_execution(agent_id: str, success: bool, is_timeout: bool = False, latency_ms: float = 0.0):
    now_str = datetime.utcnow().isoformat()
    
    with _monitor_lock:
        if agent_id not in _metrics:
            _metrics[agent_id] = {
                "success_count": 0,
                "failure_count": 0,
                "timeout_count": 0,
                "latencies": [],
                "last_success": None
            }
            
        m = _metrics[agent_id]
        if success:
            m["success_count"] += 1
            m["last_success"] = now_str
        else:
            m["failure_count"] += 1
            
        if is_timeout:
            m["timeout_count"] += 1
            
        if latency_ms > 0:
            m["latencies"].append(latency_ms)

def get_agent_health(agent_id: str) -> Dict[str, Any]:
    with _monitor_lock:
        if agent_id not in _metrics:
            return {
                "success_count": 0,
                "failure_count": 0,
                "timeout_count": 0,
                "average_latency": 0.0,
                "health_score": 1.0,
                "last_success": None
            }
            
        m = _metrics[agent_id]
        s_count = m["success_count"]
        f_count = m["failure_count"]
        t_count = m["timeout_count"]
        
        total = s_count + f_count
        success_rate = (s_count / total) if total > 0 else 1.0
        availability = 1.0 - (t_count / total if total > 0 else 0.0)
        
        avg_latency = (sum(m["latencies"]) / len(m["latencies"])) if m["latencies"] else 0.0
        latency_score = max(0.0, 1.0 - (avg_latency / 2000.0))
        
        health_score = 0.4 * success_rate + 0.3 * availability + 0.3 * latency_score
        
        return {
            "success_count": s_count,
            "failure_count": f_count,
            "timeout_count": t_count,
            "average_latency": round(avg_latency, 2),
            "health_score": round(max(0.0, min(health_score, 1.0)), 4),
            "last_success": m["last_success"]
        }

def get_all_agents_health() -> Dict[str, Dict[str, Any]]:
    with _monitor_lock:
        agents = list(_metrics.keys())
    return {a: get_agent_health(a) for a in agents}

def clear_agent_monitor():
    with _monitor_lock:
        _metrics.clear()
