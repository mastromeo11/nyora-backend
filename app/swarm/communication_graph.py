import threading
from datetime import datetime
from typing import Dict, Any

_graph_lock = threading.Lock()
_flows: Dict[tuple, Dict[str, Any]] = {}

def record_message_flow(sender: str, receiver: str, success: bool = True, latency_ms: float = 0.0):
    now_str = datetime.utcnow().isoformat()
    key = (sender, receiver)
    
    with _graph_lock:
        if key not in _flows:
            _flows[key] = {
                "frequency": 0,
                "success_count": 0,
                "latencies": [],
                "last_seen": now_str
            }
            
        flow = _flows[key]
        flow["frequency"] += 1
        if success:
            flow["success_count"] += 1
        if latency_ms > 0:
            flow["latencies"].append(latency_ms)
        flow["last_seen"] = now_str

def get_communication_graph_data() -> Dict[str, Any]:
    nodes = set()
    edges = []
    
    with _graph_lock:
        for (sender, receiver), stats in _flows.items():
            nodes.add(sender)
            nodes.add(receiver)
            
            freq = stats["frequency"]
            succ_count = stats["success_count"]
            success_rate = (succ_count / freq) if freq > 0 else 1.0
            
            recency = 1.0
            try:
                delta = datetime.utcnow() - datetime.fromisoformat(stats["last_seen"])
                recency = 1.0 / (1.0 + delta.total_seconds() / 60.0)
            except Exception:
                pass
                
            comm_strength = 0.4 * min(freq / 10.0, 1.0) + 0.3 * success_rate + 0.3 * recency
            avg_latency = (sum(stats["latencies"]) / len(stats["latencies"])) if stats["latencies"] else 0.0
            
            edges.append({
                "source": sender,
                "target": receiver,
                "frequency": freq,
                "success_rate": success_rate,
                "average_latency": avg_latency,
                "strength": round(comm_strength, 4)
            })
            
    return {
        "nodes": [{"id": name, "label": f"Agent: {name}"} for name in sorted(list(nodes))],
        "edges": edges
    }

def clear_communication_graph():
    with _graph_lock:
        _flows.clear()
