import threading
from collections import OrderedDict
from typing import Any, Optional
from app.config import MAX_AGENT_CACHE_SIZE

class LRUCache:
    def __init__(self, capacity: int = MAX_AGENT_CACHE_SIZE):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key: Any, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def clear(self):
        with self.lock:
            self.cache.clear()

    def size(self) -> int:
        with self.lock:
            return len(self.cache)

# Global Swarm Caches
negotiation_cache = LRUCache()
delegation_cache = LRUCache()
shared_memory_cache = LRUCache()
consensus_cache = LRUCache()

_hits = 0
_misses = 0

def get_agent_cache_metrics() -> dict:
    total = _hits + _misses
    hit_rate = (_hits / total) if total > 0 else 1.0
    return {
        "hits": _hits,
        "misses": _misses,
        "hit_rate": hit_rate,
        "negotiation_cache_size": negotiation_cache.size(),
        "delegation_cache_size": delegation_cache.size(),
        "shared_memory_cache_size": shared_memory_cache.size(),
        "consensus_cache_size": consensus_cache.size()
    }

def clear_all_agent_caches():
    global _hits, _misses
    negotiation_cache.clear()
    delegation_cache.clear()
    shared_memory_cache.clear()
    consensus_cache.clear()
    _hits = 0
    _misses = 0

def record_hit():
    global _hits
    _hits += 1

def record_miss():
    global _misses
    _misses += 1
