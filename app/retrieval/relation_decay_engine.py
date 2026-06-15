from app.config import (
    ENABLE_RELATION_DECAY,
    RELATION_DECAY_FACTOR,
    ENTITY_DECAY_FACTOR
)
from app.retrieval.graph_store import load_graph, save_graph

def decay_graph():
    """
    Applies temporal decay to all entity confidence scores and relation weights
    in the Knowledge Graph. This prevents historical ties from permanently dominating
    retrieval context.
    """
    if not ENABLE_RELATION_DECAY:
        print("[DECAY ENGINE] Relation decay is disabled in config.")
        return

    graph = load_graph()
    
    entities = graph.setdefault("entities", {})
    relations = graph.setdefault("relations", {})

    # 1. Decay entity confidence
    for ent_id, ent_dict in entities.items():
        old_conf = ent_dict.get("confidence", 1.0)
        ent_dict["confidence"] = round(old_conf * ENTITY_DECAY_FACTOR, 4)

    # 2. Decay relation weight and confidence
    for rel_id, rel_dict in relations.items():
        old_weight = rel_dict.get("weight", 1.0)
        old_conf = rel_dict.get("confidence", 1.0)
        
        rel_dict["weight"] = round(old_weight * RELATION_DECAY_FACTOR, 4)
        rel_dict["confidence"] = round(old_conf * RELATION_DECAY_FACTOR, 4)

    print(f"[DECAY ENGINE] Applied decay factor {RELATION_DECAY_FACTOR} to {len(relations)} relations and {ENTITY_DECAY_FACTOR} to {len(entities)} entities.")
    save_graph()
