import threading
from datetime import datetime
from typing import Dict, Any, Optional
from app.swarm.agent_cache import shared_memory_cache, record_hit, record_miss

_memory_lock = threading.Lock()
_memory_db: Dict[str, Dict[str, Any]] = {}

def write_shared_memory(key: str, value: Any, modified_by: str) -> Dict[str, Any]:
    now_str = datetime.utcnow().isoformat()
    
    with _memory_lock:
        existing = _memory_db.get(key)
        if existing:
            version = existing.get("version", 1) + 1
            created_at = existing.get("created_at")
        else:
            version = 1
            created_at = now_str
            
        node = {
            "key": key,
            "value": value,
            "version": version,
            "created_at": created_at,
            "updated_at": now_str,
            "last_modified_by": modified_by
        }
        _memory_db[key] = node
        
    # Invalidate shared memory cache on write
    shared_memory_cache.clear()
    
    # Track inside persistent store
    from app.swarm.agent_store import load_swarm_store, save_swarm_store
    store = load_swarm_store()
    store_mem = store.setdefault("shared_memory", {})
    store_mem[key] = node
    save_swarm_store()
    
    return node

def read_shared_memory(key: str) -> Optional[Dict[str, Any]]:
    # Check cache
    cached = shared_memory_cache.get(key)
    if cached is not None:
        record_hit()
        return cached
        
    record_miss()
    
    with _memory_lock:
        node = _memory_db.get(key)
        
    if node:
        shared_memory_cache.set(key, node)
    return node

def get_shared_memory_state() -> Dict[str, Any]:
    with _memory_lock:
        return dict(_memory_db)

def clear_shared_memory():
    with _memory_lock:
        _memory_db.clear()
    shared_memory_cache.clear()
