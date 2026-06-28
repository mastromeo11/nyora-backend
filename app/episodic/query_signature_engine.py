import hashlib
from typing import Set, Union, List

def generate_query_signature(query: str, entities: Union[Set[str], List[str]], intent_type: str) -> str:
    """
    Generates a deterministic hash signature for a query, entity set, and intent type.
    """
    normalized_query = " ".join(query.strip().lower().split())
    sorted_entities = sorted(list(set(entities)))
    entities_str = ",".join(sorted_entities)
    normalized_intent = intent_type.strip().lower()
    
    raw_str = f"{normalized_query}|{entities_str}|{normalized_intent}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
