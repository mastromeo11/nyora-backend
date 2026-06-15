from typing import List, Dict, Any, Set
from app.retrieval.graph_store import (
    get_entities,
    get_relations,
    append_entities,
    save_communities
)
from app.retrieval.knowledge_models import EntityNode, CommunityNode
from app.config import ENABLE_COMMUNITY_DETECTION

def detect_communities():
    """
    Runs the modularity-free centrality calculation and Label Propagation Algorithm (LPA)
    to cluster semantic graph entities into communities.
    
    Persists updated EntityNodes and newly created CommunityNodes.
    """
    if not ENABLE_COMMUNITY_DETECTION:
        print("[COMMUNITY DETECTOR] Community detection is disabled in config.")
        return

    entities = get_entities()
    relations = get_relations()

    if not entities:
        print("[COMMUNITY DETECTOR] No entities in graph to detect communities.")
        return

    entity_map = {ent.canonical_name: ent for ent in entities}

    # 1. Compute Degree and Relation Strength for Centrality
    # degree: number of connected relations
    # relation_strength: sum of relation weights/confidences
    degrees: Dict[str, int] = {ent.canonical_name: 0 for ent in entities}
    relation_strengths: Dict[str, float] = {ent.canonical_name: 0.0 for ent in entities}

    # Adjacency list for Label Propagation: node -> list of (neighbor, weight)
    adj_list: Dict[str, List[tuple]] = {ent.canonical_name: [] for ent in entities}

    for rel in relations:
        src = rel.source_entity
        tgt = rel.target_entity

        if src in entity_map and tgt in entity_map:
            degrees[src] += 1
            degrees[tgt] += 1
            relation_strengths[src] += rel.weight
            relation_strengths[tgt] += rel.weight
            
            adj_list[src].append((tgt, rel.weight))
            adj_list[tgt].append((src, rel.weight))

    # Calculate centrality_score for each entity
    # centrality_score = 0.4 * degree + 0.3 * mentions + 0.3 * relation_strength
    for ent in entities:
        canonical = ent.canonical_name
        deg = degrees[canonical]
        mentions = ent.mentions
        strength = relation_strengths[canonical]
        
        ent.centrality_score = round(0.4 * deg + 0.3 * mentions + 0.3 * strength, 4)
        # importance_score is proportional or equal to centrality for ranking
        ent.importance_score = ent.centrality_score

    # 2. Label Propagation Algorithm (LPA)
    # Initialize labels with each node's own canonical name
    labels = {ent.canonical_name: ent.canonical_name for ent in entities}
    
    # Run for a fixed number of iterations or until convergence (e.g. max 10 iterations)
    max_iterations = 10
    for iteration in range(max_iterations):
        changed = False
        # Sort node names lexicographically to ensure deterministic order and tie-breakers
        sorted_nodes = sorted(list(labels.keys()))
        
        for node in sorted_nodes:
            neighbors = adj_list[node]
            if not neighbors:
                continue
            
            # Sum label weights from neighbors
            label_weights: Dict[str, float] = {}
            for neighbor, weight in neighbors:
                neighbor_label = labels[neighbor]
                label_weights[neighbor_label] = label_weights.get(neighbor_label, 0.0) + weight
            
            # Find label(s) with maximum weight
            if not label_weights:
                continue
                
            max_weight = max(label_weights.values())
            best_labels = [lbl for lbl, w in label_weights.items() if w == max_weight]
            
            # Tie breaker: choose the lexicographically smallest label
            best_label = sorted(best_labels)[0]
            
            if labels[node] != best_label:
                labels[node] = best_label
                changed = True
                
        if not changed:
            # Stopped early due to convergence
            break

    # 3. Group Nodes into Communities
    community_groups: Dict[str, List[str]] = {}
    for node, label in labels.items():
        community_groups.setdefault(label, []).append(node)

    # 4. Process Communities
    community_nodes: List[CommunityNode] = []
    
    # Clear previous community IDs
    for ent in entities:
        ent.community_id = None

    for idx, (label, members) in enumerate(sorted(community_groups.items())):
        comm_id = f"community_{idx + 1}"
        
        # Find community center entity: member with highest centrality_score
        members_sorted = sorted(
            members,
            key=lambda m: (entity_map[m].centrality_score, m),
            reverse=True
        )
        center_entity = members_sorted[0]
        
        # Calculate community importance (average centrality_score of members)
        total_centrality = sum(entity_map[m].centrality_score for m in members)
        avg_centrality = round(total_centrality / len(members), 4)

        comm_node = CommunityNode(
            community_id=comm_id,
            entities=members,
            importance=avg_centrality,
            community_center_entity=center_entity
        )
        community_nodes.append(comm_node)

        # Set community ID on entities
        for m in members:
            entity_map[m].community_id = comm_id

    # 5. Persist Changes
    # First save communities
    save_communities(community_nodes)
    # Then update entity nodes with their new community labels, importance, and centrality scores
    append_entities(entities)
    
    print(f"[COMMUNITY DETECTOR] Completed community detection. Detected {len(community_nodes)} communities.")
