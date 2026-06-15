from typing import List, Dict, Any, Set, Tuple
from app.config import MAX_GRAPH_DEPTH, MAX_PATHS, MAX_TOTAL_VISITED
from app.retrieval.entity_alias_registry import normalize_entity_name
from app.retrieval.graph_store import get_entities, get_relations
from app.retrieval.knowledge_models import EntityNode, RelationNode
from app.retrieval.graph_cache import paths_cache, record_hit, record_miss

def find_paths(source: str, target: str, max_depth: int = None) -> List[List[Any]]:
    """
    Finds all paths between source and target entities using BFS.
    Enforces loop protection, maximum path depth, and maximum paths to prevent graph explosion.
    
    Args:
        source (str): Source entity name or ID.
        target (str): Target entity name or ID.
        max_depth (int): Optional override for MAX_GRAPH_DEPTH.
        
    Returns:
        List[List[Any]]: A list of paths, where each path is [EntityNode, RelationNode, EntityNode, ...].
    """
    if not max_depth:
        max_depth = MAX_GRAPH_DEPTH

    source_norm = normalize_entity_name(source.replace("entity_", ""))
    target_norm = normalize_entity_name(target.replace("entity_", ""))

    if not source_norm or not target_norm:
        return []

    # Check cache
    cache_key = (source_norm, target_norm, max_depth)
    cached = paths_cache.get(cache_key)
    if cached is not None:
        record_hit()
        return cached

    record_miss()

    # Retrieve current graph data
    entities_list = get_entities()
    relations_list = get_relations()

    # Index entities and relations for fast traversal
    entity_map = {ent.canonical_name: ent for ent in entities_list}
    
    # Build adjacency list: node -> list of (relation, target_node)
    adj_list: Dict[str, List[Tuple[RelationNode, str]]] = {}
    for rel in relations_list:
        src = rel.source_entity
        tgt = rel.target_entity
        
        adj_list.setdefault(src, []).append((rel, tgt))
        # Assuming undirected/bidirectional traversal for paths finder
        adj_list.setdefault(tgt, []).append((rel, src))

    if source_norm not in entity_map or target_norm not in entity_map:
        return []

    # BFS Queue: stores (current_canonical_name, path_elements, visited_nodes_in_path, visited_edges_in_path)
    # path_elements: [EntityNode, RelationNode, EntityNode, ...]
    start_node = entity_map[source_norm]
    queue = [(source_norm, [start_node], {source_norm}, set())]
    
    found_paths = []
    total_visited_count = 0

    while queue and len(found_paths) < MAX_PATHS:
        curr, path_elements, visited_nodes, visited_edges = queue.pop(0)
        total_visited_count += 1
        
        if total_visited_count > MAX_TOTAL_VISITED:
            break

        # If we reached the target, record the path
        if curr == target_norm:
            found_paths.append(path_elements)
            continue

        # Check depth limit (depth is measured by number of relations in the path)
        current_depth = len(path_elements) // 2
        if current_depth >= max_depth:
            continue

        # Traverse neighbors
        neighbors = adj_list.get(curr, [])
        for rel, neighbor in neighbors:
            # Loop protection: ensure we don't visit the same node or edge twice in a single path
            if neighbor in visited_nodes or rel.relation_id in visited_edges:
                continue

            neighbor_node = entity_map.get(neighbor)
            if not neighbor_node:
                continue

            new_path = list(path_elements) + [rel, neighbor_node]
            new_visited_nodes = set(visited_nodes)
            new_visited_nodes.add(neighbor)
            new_visited_edges = set(visited_edges)
            new_visited_edges.add(rel.relation_id)

            queue.append((neighbor, new_path, new_visited_nodes, new_visited_edges))

    # Cache results
    paths_cache.set(cache_key, found_paths)
    return found_paths
