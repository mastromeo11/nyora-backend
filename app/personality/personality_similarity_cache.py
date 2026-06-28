import threading
from collections import OrderedDict
from datetime import datetime
from typing import Optional
from app.personality.personality_models import PersonalitySimilarityNode

class PersonalitySimilarityCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, id1: str, id2: str) -> Optional[PersonalitySimilarityNode]:
        """
        Retrieves similarity node. Ordered pair normalization: (A, B) == (B, A).
        """
        sorted_ids = sorted([str(id1), str(id2)])
        key = (sorted_ids[0], sorted_ids[1])
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, id1: str, id2: str, similarity: float) -> PersonalitySimilarityNode:
        """
        Puts similarity score as PersonalitySimilarityNode. Enforces capacity.
        """
        sorted_ids = sorted([str(id1), str(id2)])
        source = sorted_ids[0]
        target = sorted_ids[1]
        key = (source, target)

        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.frequency += 1
                node.similarity = similarity
                node.last_seen = datetime.utcnow().isoformat()
                self.cache.move_to_end(key)
            else:
                node = PersonalitySimilarityNode(
                    source_personality=source,
                    target_personality=target,
                    similarity=similarity,
                    frequency=1,
                    last_seen=datetime.utcnow().isoformat()
                )
                self.cache[key] = node
                if len(self.cache) > self.capacity:
                    self.cache.popitem(last=False)

        try:
            from app.personality.personality_store import append_personality_similarity_node
            append_personality_similarity_node(node)
        except Exception as e:
            print(f"[PERSONALITY SIMILARITY CACHE] Error saving to store: {e}")

        return node

    def clear(self):
        with self.lock:
            self.cache.clear()

personality_similarity_cache = PersonalitySimilarityCache(capacity=1000)
