from app.retrieval.graph_store import load_graph, save_graph
from app.config import MIN_RELATION_CONFIDENCE

def prune_graph(weight_threshold: float = 0.1) -> dict:
    """
    Purges relations whose weights have decayed below weight_threshold,
    and removes isolated entity nodes (nodes with degree = 0).
    
    Returns:
        dict: Summary of pruned entities and relations.
    """
    graph = load_graph()
    
    entities = graph.setdefault("entities", {})
    relations = graph.setdefault("relations", {})
    
    initial_entities_count = len(entities)
    initial_relations_count = len(relations)

    # 1. Purge low-weight relations
    pruned_rel_ids = []
    for rel_id, rel in list(relations.items()):
        weight = rel.get("weight", 1.0)
        if weight < weight_threshold:
            pruned_rel_ids.append(rel_id)
            del relations[rel_id]

    # 2. Re-calculate active entity connections
    active_canonical_names = set()
    for rel in relations.values():
        active_canonical_names.add(rel["source_entity"])
        active_canonical_names.add(rel["target_entity"])

    # 3. Purge isolated entity nodes
    pruned_ent_ids = []
    for ent_id, ent in list(entities.items()):
        canonical = ent["canonical_name"]
        # Only prune if the entity is conceptual and has no connections
        if ent.get("entity_type", "conceptual") == "conceptual" and canonical not in active_canonical_names:
            pruned_ent_ids.append(ent_id)
            del entities[ent_id]

    pruned_entities = len(pruned_ent_ids)
    pruned_relations = len(pruned_rel_ids)
    
    # Pruning efficiency metric: ratio of pruned elements to total initial elements
    total_initial = initial_entities_count + initial_relations_count
    total_pruned = pruned_entities + pruned_relations
    pruning_efficiency = (total_pruned / total_initial) if total_initial > 0 else 0.0

    print(f"[GRAPH PRUNER] Pruned {pruned_relations} relations below threshold {weight_threshold}.")
    print(f"[GRAPH PRUNER] Pruned {pruned_entities} isolated entities.")
    
    if total_pruned > 0:
        save_graph()
        
    return {
        "initial_entities": initial_entities_count,
        "initial_relations": initial_relations_count,
        "pruned_entities": pruned_entities,
        "pruned_relations": pruned_relations,
        "pruning_efficiency": pruning_efficiency
    }
