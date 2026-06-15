from typing import List, Dict, Any, Optional
from app.retrieval.entity_alias_registry import normalize_entity_name
from app.retrieval.graph_store import (
    get_entities,
    get_relations,
    get_temporal_events,
    get_communities
)
from app.retrieval.knowledge_models import EntityNode, RelationNode, TemporalNode, CommunityNode
from app.retrieval.graph_cache import (
    neighbors_cache,
    communities_cache,
    subgraphs_cache,
    record_hit,
    record_miss
)
from app.retrieval.graph_traverser import find_paths
from app.retrieval.graph_embedding_engine import (
    get_node_embedding,
    calculate_cosine_similarity
)

def query_neighbors(entity: str) -> List[Dict[str, Any]]:
    """
    Finds all direct neighbor nodes and the relations connecting them to the target entity.
    Uses caching.
    """
    canonical = normalize_entity_name(entity.replace("entity_", ""))
    if not canonical:
        return []

    cached = neighbors_cache.get(canonical)
    if cached is not None:
        record_hit()
        return cached

    record_miss()

    entities = get_entities()
    relations = get_relations()

    entity_map = {ent.canonical_name: ent for ent in entities}
    if canonical not in entity_map:
        return []

    neighbors = []
    for rel in relations:
        neighbor_name = None
        direction = None
        
        if rel.source_entity == canonical:
            neighbor_name = rel.target_entity
            direction = "outgoing"
        elif rel.target_entity == canonical:
            neighbor_name = rel.source_entity
            direction = "incoming"

        if neighbor_name and neighbor_name in entity_map:
            neighbors.append({
                "neighbor": entity_map[neighbor_name],
                "relation": rel,
                "direction": direction
            })

    neighbors_cache.set(canonical, neighbors)
    return neighbors

def query_path(source: str, target: str, max_depth: int = None) -> List[List[Any]]:
    """
    Finds paths between source and target entities. Delegates to the traverser.
    """
    return find_paths(source, target, max_depth=max_depth)

def query_community(entity: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the community details (members, center, importance) that the entity belongs to.
    """
    canonical = normalize_entity_name(entity.replace("entity_", ""))
    if not canonical:
        return None

    cached = communities_cache.get(canonical)
    if cached is not None:
        record_hit()
        return cached

    record_miss()

    entities = get_entities()
    entity_map = {ent.canonical_name: ent for ent in entities}
    if canonical not in entity_map:
        return None

    target_entity = entity_map[canonical]
    community_id = target_entity.community_id
    if not community_id:
        return None

    communities = get_communities()
    target_community = None
    for comm in communities:
        if comm.community_id == community_id:
            target_community = comm
            break

    if not target_community:
        return None

    # Gather nodes belonging to this community
    community_nodes = [entity_map[ent] for ent in target_community.entities if ent in entity_map]

    res = {
        "community_id": community_id,
        "importance": target_community.importance,
        "community_center_entity": target_community.community_center_entity,
        "entities": community_nodes
    }

    communities_cache.set(canonical, res)
    return res

def query_timeline(entity: str) -> List[TemporalNode]:
    """
    Retrieves a chronological sequence of events associated with the target entity.
    """
    canonical = normalize_entity_name(entity.replace("entity_", ""))
    if not canonical:
        return []

    events = get_temporal_events()
    matched_events = []
    for event in events:
        # Check if the canonical entity name is in the event entities
        # event.entities contains canonical names
        if any(normalize_entity_name(e) == canonical for e in event.entities):
            matched_events.append(event)

    # Sort chronological (oldest first) based on timestamp ISO string
    matched_events.sort(key=lambda x: x.timestamp)
    return matched_events

def query_similar(entity: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Calculates cosine similarity between the target entity's text vector and all other entities,
    returning a ranked recommendation list.
    """
    canonical = normalize_entity_name(entity.replace("entity_", ""))
    if not canonical:
        return []

    entities = get_entities()
    entity_map = {ent.canonical_name: ent for ent in entities}
    if canonical not in entity_map:
        return []

    target_ent = entity_map[canonical]
    try:
        target_vec = get_node_embedding(target_ent.entity_id, target_ent.name, target_ent.entity_type)
    except Exception as e:
        print(f"Error getting embedding for {canonical}: {e}")
        return []

    recommendations = []
    for ent in entities:
        if ent.canonical_name == canonical:
            continue
        try:
            ent_vec = get_node_embedding(ent.entity_id, ent.name, ent.entity_type)
            sim = calculate_cosine_similarity(target_vec, ent_vec)
            recommendations.append({
                "entity": ent,
                "similarity": sim
            })
        except Exception as e:
            print(f"Error computing similarity for {ent.canonical_name}: {e}")
            continue

    recommendations.sort(key=lambda x: x["similarity"], reverse=True)
    return recommendations[:top_n]
