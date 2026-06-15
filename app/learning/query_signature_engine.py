import hashlib
from typing import Set

def generate_query_signature(query: str, entity_set: Set[str], intent_type: str) -> str:
    """
    Generates a deterministic hash representing a query signature.
    Prevents duplicate pattern nodes from polluting memory.
    """
    # 1. Normalize query
    normalized_query = query.strip().lower()
    
    # 2. Sort entities to ensure determinism
    sorted_entities = sorted(list(entity_set))
    entities_str = ",".join(sorted_entities)
    
    # 3. Intent type string representation
    intent = str(intent_type).strip().lower()
    
    # 4. Combine key signature components
    combined = f"query:{normalized_query}|entities:{entities_str}|intent:{intent}"
    
    # 5. Generate SHA-256 hash representation
    signature_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    return f"sig_{signature_hash[:16]}"
