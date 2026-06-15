import threading
from collections import OrderedDict
from typing import Any, Optional
from app.config import LEARNING_CACHE_SIZE

class LRUCache:
    """
    A simple thread-safe LRU Cache implementation using OrderedDict.
    """
    def __init__(self, capacity: int = LEARNING_CACHE_SIZE):
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

# Global LRU Caches for learning structures
pattern_cache = LRUCache()
failure_cache = LRUCache()
cluster_cache = LRUCache()
feedback_cache = LRUCache()
correction_cache = LRUCache()

_hits = 0
_misses = 0

def get_learning_cache_metrics() -> dict:
    """
    Returns hit rate and cache sizes.
    """
    total = _hits + _misses
    hit_rate = (_hits / total) if total > 0 else 1.0
    return {
        "hits": _hits,
        "misses": _misses,
        "hit_rate": hit_rate,
        "pattern_cache_size": pattern_cache.size(),
        "failure_cache_size": failure_cache.size(),
        "cluster_cache_size": cluster_cache.size(),
        "feedback_cache_size": feedback_cache.size(),
        "correction_cache_size": correction_cache.size()
    }

def clear_all_learning_caches():
    """
    Invalidates all continual learning caches and resets metrics.
    """
    global _hits, _misses
    pattern_cache.clear()
    failure_cache.clear()
    cluster_cache.clear()
    feedback_cache.clear()
    correction_cache.clear()
    _hits = 0
    _misses = 0

def record_hit():
    global _hits
    _hits += 1

def record_miss():
    global _misses
    _misses += 1
