from app.retrieval.evidence_graph import get_node_entities

def calculate_importance(query: str, answer: str, citations: list, confidence_score: float) -> float:
    """
    Computes numerical importance score for a conversation turn.
    importance_score = 0.4 * entity_count + 0.3 * citation_count + 0.3 * confidence_score
    """
    # 1. Count unique entities in query and answer combined
    entities = get_node_entities(query).union(get_node_entities(answer))
    entity_count = len(entities)
    
    # 2. Count citation sources
    citation_count = len(citations)
    
    # 3. Calculate score
    score = 0.4 * entity_count + 0.3 * citation_count + 0.3 * confidence_score
    return round(score, 4)
