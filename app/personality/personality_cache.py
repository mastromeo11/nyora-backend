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

preferences_cache = LRUCache(100)
styles_cache = LRUCache(100)
personalities_cache = LRUCache(100)
summaries_cache = LRUCache(100)
archives_cache = LRUCache(100)

def clear_all_personality_caches():
    """
    Clears all active personality, style, preference, and similarity caches.
    """
    preferences_cache.clear()
    styles_cache.clear()
    personalities_cache.clear()
    summaries_cache.clear()
    archives_cache.clear()
    
    try:
        from app.personality.personality_similarity_cache import personality_similarity_cache
        personality_similarity_cache.clear()
    except ImportError:
        pass
