from datetime import datetime
from app.retrieval.memory_models import MemoryNode
from app.retrieval.evidence_graph import get_node_entities
from app.retrieval.relevance_filter import extract_substantive_keywords

def rank_memory_nodes(nodes: list, query: str) -> list:
    """
    Ranks memory nodes using the standard formula:
    memory_score = 0.40 * recency + 0.30 * entity_overlap + 0.20 * conversation_similarity + 0.10 * importance
    
    Returns the sorted list of nodes.
    """
    ranked_nodes = []
    query_entities = get_node_entities(query)
    query_keywords = extract_substantive_keywords(query)
    now = datetime.utcnow()
    
    for node in nodes:
        # 1. Recency
        try:
            ts = datetime.fromisoformat(node.timestamp.replace("Z", "+00:00"))
            # remove timezone info to make it naive
            ts = ts.replace(tzinfo=None)
            age_seconds = (now - ts).total_seconds()
            # 1 minute half-life scaling
            recency = 1.0 / (1.0 + max(0.0, age_seconds) / 60.0)
        except Exception:
            recency = 0.5
            
        # 2. Entity Overlap
        node_entities = get_node_entities(node.content)
        if query_entities:
            overlap = len(query_entities.intersection(node_entities))
            entity_overlap = overlap / len(query_entities)
        else:
            entity_overlap = 0.0
            
        # 3. Conversation Similarity (Jaccard on substantive keywords)
        node_keywords = extract_substantive_keywords(node.content)
        union_kws = query_keywords.union(node_keywords)
        if union_kws:
            sim = len(query_keywords.intersection(node_keywords)) / len(union_kws)
            conversation_similarity = sim
        else:
            conversation_similarity = 0.0
            
        # 4. Importance
        importance = node.importance
        
        # Calculate final score
        score = (
            0.40 * recency +
            0.30 * entity_overlap +
            0.20 * conversation_similarity +
            0.10 * importance
        )
        
        node.score = round(score, 4)
        ranked_nodes.append(node)
        
    # Sort descending by score
    ranked_nodes.sort(key=lambda x: x.score, reverse=True)
    return ranked_nodes
