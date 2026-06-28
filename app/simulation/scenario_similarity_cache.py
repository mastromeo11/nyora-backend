import threading
from collections import OrderedDict
from typing import Optional

_cache_lock = threading.Lock()
_similarity_cache = OrderedDict()
MAX_CACHE_SIZE = 1000

def _get_cache_key(id_a: str, id_b: str) -> str:
    # Ensure order doesn't matter for similarity lookup
    low = min(id_a, id_b)
    high = max(id_a, id_b)
    return f"{low}_to_{high}"

def get_similarity(id_a: str, id_b: str) -> Optional[float]:
    key = _get_cache_key(id_a, id_b)
    with _cache_lock:
        if key in _similarity_cache:
            # Move to end (MRU)
            val = _similarity_cache.pop(key)
            _similarity_cache[key] = val
            return val
    return None

def set_similarity(id_a: str, id_b: str, score: float):
    key = _get_cache_key(id_a, id_b)
    with _cache_lock:
        if key in _similarity_cache:
            _similarity_cache.pop(key)
        _similarity_cache[key] = score
        if len(_similarity_cache) > MAX_CACHE_SIZE:
            _similarity_cache.popitem(last=False) # pop oldest (FIFO/LRU)

def clear_similarity_cache():
    with _cache_lock:
        _similarity_cache.clear()
