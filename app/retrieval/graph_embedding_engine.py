import numpy as np
from typing import List, Dict, Any, Optional
from app.embedding.text_embedder import embed_text

# In-memory caches for node and relation embeddings to avoid redundant calculations
_node_vector_cache: Dict[str, List[float]] = {}
_relation_vector_cache: Dict[str, List[float]] = {}

def get_node_embedding(node_id: str, label: str, node_type: str) -> List[float]:
    """
    Retrieves or calculates the BGE embedding for a node based on its type and description.
    """
    if node_id in _node_vector_cache:
        return _node_vector_cache[node_id]

    # Formulate a descriptive text representation for the node
    text_to_embed = f"Node type: {node_type}. Name: {label}."
    
    # Generate embedding
    embedding = embed_text([text_to_embed])[0]
    _node_vector_cache[node_id] = embedding
    return embedding

def get_relation_embedding(relation_id: str, source: str, target: str, rel_type: str) -> List[float]:
    """
    Retrieves or calculates the BGE embedding for a relation.
    """
    if relation_id in _relation_vector_cache:
        return _relation_vector_cache[relation_id]

    # Formulate a descriptive text representation for the relation
    text_to_embed = f"Relation: {source} {rel_type} {target}."
    
    # Generate embedding
    embedding = embed_text([text_to_embed])[0]
    _relation_vector_cache[relation_id] = embedding
    return embedding

def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Computes cosine similarity between two normalized vectors.
    Since embed_text normalizes embeddings, this is just a dot product.
    """
    if not vec1 or not vec2:
        return 0.0
    # Dot product
    return float(np.dot(vec1, vec2))

def get_query_embedding(query: str) -> List[float]:
    """
    Wraps embed_text to get a query vector.
    """
    return embed_text([query])[0]

def clear_embedding_caches():
    """
    Clears the cached node and relation embeddings.
    """
    _node_vector_cache.clear()
    _relation_vector_cache.clear()
