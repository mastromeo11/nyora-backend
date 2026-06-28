import threading
from collections import OrderedDict
from typing import Any, Optional
from app.config import EPISODE_CACHE_SIZE

class LRUCache:
    def __init__(self, capacity: int = EPISODE_CACHE_SIZE):
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

# Global episodic caches
episode_cache = LRUCache()
replay_cache = LRUCache()
chain_cache = LRUCache()
summary_cache = LRUCache()
cluster_cache = LRUCache()

_hits = 0
_misses = 0

def get_episodic_cache_metrics() -> dict:
    total = _hits + _misses
    hit_rate = (_hits / total) if total > 0 else 1.0
    return {
        "hits": _hits,
        "misses": _misses,
        "hit_rate": hit_rate,
        "episode_cache_size": episode_cache.size(),
        "replay_cache_size": replay_cache.size(),
        "chain_cache_size": chain_cache.size(),
        "summary_cache_size": summary_cache.size(),
        "cluster_cache_size": cluster_cache.size()
    }

def clear_all_episodic_caches():
    global _hits, _misses
    episode_cache.clear()
    replay_cache.clear()
    chain_cache.clear()
    summary_cache.clear()
    cluster_cache.clear()
    _hits = 0
    _misses = 0

def record_episodic_hit():
    global _hits
    _hits += 1

def record_episodic_miss():
    global _misses
    _misses += 1
