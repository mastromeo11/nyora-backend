import threading
from collections import OrderedDict
from typing import Any, Optional
from app.config import GRAPH_CACHE_SIZE

class LRUCache:
    """
    A simple thread-safe LRU Cache implementation using OrderedDict.
    """
    def __init__(self, capacity: int = GRAPH_CACHE_SIZE):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            # Move to end to represent recently used
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

# Global LRU Caches for the Knowledge Graph
neighbors_cache = LRUCache()
paths_cache = LRUCache()
communities_cache = LRUCache()
subgraphs_cache = LRUCache()

# Latency tracking stats for the cache (for metrics reporting)
_hits = 0
_misses = 0

def get_cache_metrics() -> dict:
    """
    Returns hit rate and cache sizes.
    """
    total = _hits + _misses
    hit_rate = (_hits / total) if total > 0 else 1.0
    return {
        "hits": _hits,
        "misses": _misses,
        "hit_rate": hit_rate,
        "neighbors_cache_size": neighbors_cache.size(),
        "paths_cache_size": paths_cache.size(),
        "communities_cache_size": communities_cache.size(),
        "subgraphs_cache_size": subgraphs_cache.size()
    }

def clear_all_graph_caches():
    """
    Invalidates all knowledge graph caches and resets metrics.
    """
    global _hits, _misses
    neighbors_cache.clear()
    paths_cache.clear()
    communities_cache.clear()
    subgraphs_cache.clear()
    _hits = 0
    _misses = 0

def record_hit():
    global _hits
    _hits += 1

def record_miss():
    global _misses
    _misses += 1
