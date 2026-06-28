import threading
from collections import OrderedDict
from datetime import datetime
from typing import Optional
from app.meta.meta_models import PolicySimilarityNode

class PolicySimilarityCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, policy_a: str, policy_b: str) -> Optional[PolicySimilarityNode]:
        """
        Retrieves the similarity node from the cache. Normalizes key order so (A, B) == (B, A).
        """
        sorted_keys = sorted([str(policy_a), str(policy_b)])
        key = (sorted_keys[0], sorted_keys[1])
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, policy_a: str, policy_b: str, similarity: float) -> PolicySimilarityNode:
        """
        Puts a similarity score into the cache as a PolicySimilarityNode, enforcing capacity bounds.
        """
        sorted_keys = sorted([str(policy_a), str(policy_b)])
        source = sorted_keys[0]
        target = sorted_keys[1]
        key = (source, target)

        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.frequency += 1
                node.similarity = similarity
                node.timestamp = datetime.utcnow().isoformat()
                self.cache.move_to_end(key)
            else:
                node = PolicySimilarityNode(
                    source_policy=source,
                    target_policy=target,
                    similarity=similarity,
                    timestamp=datetime.utcnow().isoformat(),
                    frequency=1
                )
                self.cache[key] = node
                if len(self.cache) > self.capacity:
                    self.cache.popitem(last=False)

        # Persist to database store asynchronously (avoiding circular imports)
        try:
            from app.meta.meta_store import append_similarity_node
            append_similarity_node(node)
        except Exception as e:
            print(f"[SIMILARITY CACHE] Error persisting similarity node: {e}")

        return node

    def clear(self):
        with self.lock:
            self.cache.clear()

similarity_cache = PolicySimilarityCache(capacity=1000)
