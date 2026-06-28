import threading
from collections import OrderedDict
from typing import Optional, Any

class LRUCache:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def clear(self):
        with self.lock:
            self.cache.clear()

# LRU Cache Instances
tools_cache = LRUCache(100)
policies_cache = LRUCache(100)
reflections_cache = LRUCache(100)
strategies_cache = LRUCache(100)
summaries_cache = LRUCache(100)

def clear_all_policy_caches():
    """
    Clears all active policy, tool, strategy, and similarity caches.
    """
    tools_cache.clear()
    policies_cache.clear()
    reflections_cache.clear()
    strategies_cache.clear()
    summaries_cache.clear()
    
    try:
        from app.meta.policy_similarity_cache import similarity_cache
        similarity_cache.clear()
    except ImportError:
        pass
