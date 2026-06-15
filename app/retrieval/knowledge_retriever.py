from datetime import datetime
from typing import List, Dict, Any, Set
from app.config import (
    ENABLE_KNOWLEDGE_GRAPH,
    MAX_ENTITY_NEIGHBORS,
    GRAPH_WEIGHT,
    MIN_RELATION_CONFIDENCE
)
from app.retrieval.entity_alias_registry import get_canonical_entities, normalize_entity_name
from app.retrieval.graph_store import (
    get_entities,
    get_relations,
    get_temporal_events,
    get_communities
)
from app.retrieval.knowledge_models import EntityNode, RelationNode, TemporalNode
from app.retrieval.graph_embedding_engine import (
    get_node_embedding,
    get_query_embedding,
    calculate_cosine_similarity
)
from app.retrieval.graph_traverser import find_paths
from app.retrieval.graph_explanation_engine import compile_graph_explanation

def retrieve_knowledge(query: str, session_id: str = "default_session") -> dict:
    """
    Performs hybrid graph retrieval:
    1. Extracts explicit entities via alias/regex match.
    2. Performs vector-similarity semantic search across all graph nodes.
    3. Combines candidates and ranks them using:
       score = 0.30*similarity + 0.25*relation_strength + 0.20*recency + 0.15*community_importance + 0.10*entity_frequency
    4. Gathers relevant relations, multi-hop paths, and event timelines.
    5. Returns structured KG context and invokes explanation compiler.
    """
    if not ENABLE_KNOWLEDGE_GRAPH:
        return {
            "entities": [],
            "relations": [],
            "paths": [],
            "timeline": [],
            "natural_explanation": "Knowledge graph is disabled."
        }

    # 1. Exact alias matching from query
    explicit_canonicals = get_canonical_entities(query)
    
    # 2. Semantic search against all nodes
    entities = get_entities()
    relations = get_relations()
    communities = get_communities()

    if not entities:
        return {
            "entities": [],
            "relations": [],
            "paths": [],
            "timeline": [],
            "natural_explanation": "Knowledge graph is empty."
        }

    entity_map = {ent.canonical_name: ent for ent in entities}
    community_map = {c.community_id: c for c in communities}

    # Build adjacency mapping to calculate node-specific relation strengths on the fly
    adj_weights: Dict[str, List[float]] = {ent.canonical_name: [] for ent in entities}
    for rel in relations:
        src, tgt = rel.source_entity, rel.target_entity
        if src in adj_weights:
            adj_weights[src].append(rel.weight)
        if tgt in adj_weights:
            adj_weights[tgt].append(rel.weight)

    # Get query embedding
    try:
        query_vec = get_query_embedding(query)
    except Exception as e:
        print(f"[KG RETRIEVER] Query embedding error: {e}")
        query_vec = None

    # Calculate candidate scoring
    candidates = []
    now = datetime.utcnow()

    for ent in entities:
        canonical = ent.canonical_name
        
        # Calculate similarity
        similarity = 0.0
        if query_vec:
            try:
                node_vec = get_node_embedding(ent.entity_id, ent.name, ent.entity_type)
                similarity = calculate_cosine_similarity(query_vec, node_vec)
            except Exception:
                pass
        
        # Boost similarity for exact keyword match
        if canonical in explicit_canonicals:
            similarity = max(similarity, 0.95)

        # Skip candidates with very low similarity unless they were explicitly matched
        if similarity < 0.35 and canonical not in explicit_canonicals:
            continue

        # 0.25 * relation_strength (normalized sum of weights connected to the entity)
        rel_list = adj_weights.get(canonical, [])
        sum_rel_weight = sum(rel_list)
        relation_strength = min(sum_rel_weight / 5.0, 1.0)  # capped normalization

        # 0.20 * recency
        recency = 1.0
        try:
            delta = now - datetime.fromisoformat(ent.last_seen)
            delta_hours = delta.total_seconds() / 3600.0
            recency = 1.0 / (1.0 + delta_hours)
        except Exception:
            pass

        # 0.15 * community_importance
        comm_importance = 0.0
        if ent.community_id and ent.community_id in community_map:
            comm_importance = community_map[ent.community_id].importance
            # normalize if needed (community importance is avg centrality, capped at 1.0 for ranking safety)
            comm_importance = min(comm_importance / 10.0, 1.0)

        # 0.10 * entity_frequency (based on mentions count)
        entity_frequency = min(ent.mentions / 10.0, 1.0)

        # Composite score calculation
        score = (
            0.30 * similarity +
            0.25 * relation_strength +
            0.20 * recency +
            0.15 * comm_importance +
            0.10 * entity_frequency
        )
        score = round(score, 4)

        candidates.append((score, ent))

    # Sort descending by composite score
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Select top N entities
    top_candidates = candidates[:MAX_ENTITY_NEIGHBORS]
    selected_entities = [item[1] for item in top_candidates]
    selected_canonicals = {ent.canonical_name for ent in selected_entities}

    # 4. Gather relevant relations connecting selected entities
    selected_relations = []
    for rel in relations:
        if rel.source_entity in selected_canonicals and rel.target_entity in selected_canonicals:
            selected_relations.append(rel)

    # 5. Gather multi-hop paths between top 3 central entities
    top_3_canonicals = [ent.canonical_name for ent in selected_entities[:3]]
    paths = []
    for i in range(len(top_3_canonicals)):
        for j in range(i + 1, len(top_3_canonicals)):
            src = top_3_canonicals[i]
            tgt = top_3_canonicals[j]
            paths_found = find_paths(src, tgt, max_depth=2)
            paths.extend(paths_found)

    # 6. Gather associated timelines
    temporal_events = get_temporal_events()
    selected_timeline = []
    for event in temporal_events:
        # Check if event mentions any of the selected canonicals
        if any(normalize_entity_name(e) in selected_canonicals for e in event.entities):
            selected_timeline.append(event)
    selected_timeline.sort(key=lambda x: x.timestamp)

    # 7. Compile natural explanations
    explanation_diag = compile_graph_explanation(paths, neighbors=[
        {"neighbor": ent, "relation": rel, "direction": "outgoing" if rel.source_entity == ent.canonical_name else "incoming"}
        for ent in selected_entities for rel in selected_relations if rel.source_entity == ent.canonical_name or rel.target_entity == ent.canonical_name
    ][:10])  # limit neighbors passed to explanation to keep it concise

    return {
        "entities": [ent.dict() for ent in selected_entities],
        "relations": [rel.dict() for rel in selected_relations],
        "paths": [[(e.dict() if hasattr(e, "dict") else e) for e in p] for p in paths],
        "timeline": [evt.dict() for evt in selected_timeline],
        "natural_explanation": explanation_diag.get("natural_summary", "")
    }
