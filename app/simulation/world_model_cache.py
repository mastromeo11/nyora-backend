import threading
from collections import OrderedDict
from typing import Any, Optional
from app.config import SIMULATION_CACHE_SIZE

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def put(self, key: Any, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def clear(self):
        with self.lock:
            self.cache.clear()

# Global Caches
state_cache = LRUCache(SIMULATION_CACHE_SIZE)
scenario_cache = LRUCache(SIMULATION_CACHE_SIZE)
simulation_cache = LRUCache(SIMULATION_CACHE_SIZE)
policy_cache = LRUCache(SIMULATION_CACHE_SIZE)
hypothesis_cache = LRUCache(SIMULATION_CACHE_SIZE)
forecast_cache = LRUCache(SIMULATION_CACHE_SIZE)

def clear_all_simulation_caches():
    """
    Clears all cache elements upon database writes to avoid stale reads.
    """
    state_cache.clear()
    scenario_cache.clear()
    simulation_cache.clear()
    policy_cache.clear()
    hypothesis_cache.clear()
    forecast_cache.clear()
    from app.simulation.scenario_similarity_cache import clear_similarity_cache
    clear_similarity_cache()

def get_cache_hit_rate() -> float:
    """
    Computes global cache hit rate.
    """
    total_hits = (state_cache.hits + scenario_cache.hits + 
                  simulation_cache.hits + policy_cache.hits + 
                  hypothesis_cache.hits + forecast_cache.hits)
    total_misses = (state_cache.misses + scenario_cache.misses + 
                    simulation_cache.misses + policy_cache.misses + 
                    hypothesis_cache.misses + forecast_cache.misses)
    
    total_requests = total_hits + total_misses
    if total_requests == 0:
        return 1.0
    return total_hits / total_requests
