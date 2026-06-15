from typing import List, Dict, Any, Optional
from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.config import MAX_TASK_MEMORY

# Track task memory statistics in metrics
_task_mem_hits = 0
_task_mem_queries = 0

def increment_task_mem_query():
    global _task_mem_queries
    _task_mem_queries += 1

def increment_task_mem_hit():
    global _task_mem_hits
    _task_mem_hits += 1

def get_task_mem_hit_rate() -> float:
    global _task_mem_hits, _task_mem_queries
    if _task_mem_queries > 0:
        return round(_task_mem_hits / _task_mem_queries, 4)
    return 0.0

def save_task_execution(
    session_id: str,
    query: str,
    tasks: List[Any],
    results: Dict[str, Any],
    executed_tools: List[Any] = None,
    observations: List[Any] = None,
    reflections: List[Any] = None
):
    """
    Stores execution traces of subtasks and their outputs.
    """
    cache = get_session_cache(session_id)
    task_mem = cache.setdefault("task_memory", {})
    
    normalized_query = query.strip().lower()
    
    task_mem[normalized_query] = {
        "tasks": [t.dict() if hasattr(t, "dict") else t for t in tasks],
        "results": results,
        "executed_tools": [t.dict() if hasattr(t, "dict") else t for t in executed_tools] if executed_tools else [],
        "observations": [o.dict() if hasattr(o, "dict") else o for o in observations] if observations else [],
        "reflections": [r.dict() if hasattr(r, "dict") else r for r in reflections] if reflections else []
    }
    
    # Enforce MAX_TASK_MEMORY
    if len(task_mem) > MAX_TASK_MEMORY:
        # Simple pop of the first key (FIFO)
        first_key = next(iter(task_mem))
        task_mem.pop(first_key)
        
    save_session_cache(session_id, cache)
    print(f"[TASK MEMORY] Saved task execution results for query: '{query}'")

def get_cached_tasks(session_id: str, query: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves previously run tasks and outputs matching query intent.
    """
    increment_task_mem_query()
    cache = get_session_cache(session_id)
    task_mem = cache.get("task_memory", {})
    
    normalized_query = query.strip().lower()
    if normalized_query in task_mem:
        increment_task_mem_hit()
        print(f"[TASK MEMORY] Cache hit for task pattern: '{query}'")
        return task_mem[normalized_query]
        
    return None
