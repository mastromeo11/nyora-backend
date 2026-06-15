import uuid
from typing import Any, Dict, List, Optional
from app.retrieval.memory_cache import get_session_cache, save_session_cache

# Track trace cache hits in metrics
_trace_cache_hits = 0
_trace_cache_queries = 0

def increment_trace_cache_query():
    global _trace_cache_queries
    _trace_cache_queries += 1

def increment_trace_cache_hit():
    global _trace_cache_hits
    _trace_cache_hits += 1

def get_trace_cache_hit_rate() -> float:
    global _trace_cache_hits, _trace_cache_queries
    if _trace_cache_queries > 0:
        return round(_trace_cache_hits / _trace_cache_queries, 4)
    return 0.0

def save_trace(
    session_id: str,
    query: str,
    goal_dict: dict,
    plan_dict: dict,
    success: bool
):
    """
    Caches a successful execution trace (Goal, Plan, Steps, status) in the session data.
    """
    cache = get_session_cache(session_id)
    trace_cache = cache.setdefault("trace_cache", {})
    
    normalized_query = query.strip().lower()
    
    trace_cache[normalized_query] = {
        "trace_id": f"trace_{uuid.uuid4().hex[:8]}",
        "goal_id": goal_dict.get("goal_id") if goal_dict else "",
        "plan_id": plan_dict.get("plan_id") if plan_dict else "",
        "steps": plan_dict.get("steps") if plan_dict else [],
        "success": success,
        "goal": goal_dict,
        "plan": plan_dict
    }
    
    save_session_cache(session_id, cache)
    print(f"[TRACE CACHE] Cached successful execution trace for query: '{query}'")

def get_cached_trace(session_id: str, query: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a cached trace for a normalized query if it exists.
    """
    increment_trace_cache_query()
    cache = get_session_cache(session_id)
    trace_cache = cache.get("trace_cache", {})
    
    normalized_query = query.strip().lower()
    
    if normalized_query in trace_cache:
        increment_trace_cache_hit()
        print(f"[TRACE CACHE] Cache hit for query: '{query}'")
        return trace_cache[normalized_query]
        
    return None
