import threading
from collections import OrderedDict
from typing import Optional, Any

class UILRUCache:
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

# Global UI Cache Stores
theme_cache = UILRUCache(capacity=50)
dashboard_cache = UILRUCache(capacity=10)
graph_cache = UILRUCache(capacity=20)
workspace_cache = UILRUCache(capacity=100)

def clear_all_ui_caches():
    """
    Clears all active UI cache components.
    """
    theme_cache.clear()
    dashboard_cache.clear()
    graph_cache.clear()
    workspace_cache.clear()
