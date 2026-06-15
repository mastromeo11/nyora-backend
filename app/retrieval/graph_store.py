import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.retrieval.knowledge_models import EntityNode, RelationNode, TemporalNode, CommunityNode
from app.retrieval.graph_migrations import run_migrations
from app.retrieval.graph_cache import clear_all_graph_caches

GRAPH_FILE_PATH = os.path.abspath("storage/knowledge_graph.json")

# In-memory graph representation
_global_graph: Dict[str, Any] = {
    "schema_version": 1,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "entities": {},
    "relations": {},
    "communities": {},
    "subgraphs": {},
    "temporal_events": []
}

def load_graph() -> Dict[str, Any]:
    """
    Loads and migrates the persistent Knowledge Graph file.
    """
    global _global_graph
    os.makedirs(os.path.dirname(GRAPH_FILE_PATH), exist_ok=True)
    
    if os.path.exists(GRAPH_FILE_PATH):
        try:
            with open(GRAPH_FILE_PATH, "r") as f:
                data = json.load(f)
                _global_graph = run_migrations(data)
                print(f"[GRAPH STORE] Loaded Knowledge Graph. Entities: {len(_global_graph.get('entities', {}))}, Relations: {len(_global_graph.get('relations', {}))}")
        except Exception as e:
            print(f"[GRAPH STORE] Error loading graph file: {e}. Using default empty graph.")
    else:
        save_graph()
        
    return _global_graph

def save_graph():
    """
    Saves the in-memory graph representation to disk.
    """
    global _global_graph
    os.makedirs(os.path.dirname(GRAPH_FILE_PATH), exist_ok=True)
    _global_graph["updated_at"] = datetime.utcnow().isoformat()
    try:
        with open(GRAPH_FILE_PATH, "w") as f:
            json.dump(_global_graph, f, indent=4)
        print("[GRAPH STORE] Saved Knowledge Graph.")
        clear_all_graph_caches()
    except Exception as e:
        print(f"[GRAPH STORE] Error saving graph file: {e}")

def get_entities() -> List[EntityNode]:
    """
    Returns all EntityNodes in the graph.
    """
    load_graph()
    nodes = []
    for data in _global_graph.get("entities", {}).values():
        nodes.append(EntityNode(**data))
    return nodes

def get_relations() -> List[RelationNode]:
    """
    Returns all RelationNodes in the graph.
    """
    load_graph()
    rels = []
    for data in _global_graph.get("relations", {}).values():
        rels.append(RelationNode(**data))
    return rels

def get_temporal_events() -> List[TemporalNode]:
    """
    Returns all TemporalNodes in the graph.
    """
    load_graph()
    events = []
    for data in _global_graph.get("temporal_events", []):
        events.append(TemporalNode(**data))
    return events

def get_communities() -> List[CommunityNode]:
    """
    Returns all CommunityNodes in the graph.
    """
    load_graph()
    comms = []
    for data in _global_graph.get("communities", {}).values():
        comms.append(CommunityNode(**data))
    return comms

def append_entities(entity_nodes: List[EntityNode]):
    """
    Incrementally inserts or merges EntityNodes.
    """
    load_graph()
    entities = _global_graph.setdefault("entities", {})
    now_str = datetime.utcnow().isoformat()
    
    for node in entity_nodes:
        ent_id = node.entity_id
        if ent_id in entities:
            # Incremental merge
            existing = entities[ent_id]
            existing["mentions"] += node.mentions
            existing["aliases"] = list(set(existing.get("aliases", []) + node.aliases))
            existing["sources"] = list(set(existing.get("sources", []) + node.sources))
            existing["supporting_modalities"] = list(set(existing.get("supporting_modalities", []) + node.supporting_modalities))
            existing["updated_at"] = now_str
            existing["last_seen"] = now_str
            
            # Merge centrality, importance and community ID if updated
            existing["importance_score"] = node.importance_score if node.importance_score != 0.0 else existing.get("importance_score", 0.0)
            existing["centrality_score"] = node.centrality_score if node.centrality_score != 0.0 else existing.get("centrality_score", 0.0)
            existing["community_id"] = node.community_id if node.community_id is not None else existing.get("community_id")
            
            # Recalculate confidence
            support = min(len(existing["sources"]) / 5.0, 1.0) if existing["sources"] else 0.0
            consensus = min(len(existing["supporting_modalities"]) / 3.0, 1.0) if existing["supporting_modalities"] else 0.0
            freq = min(existing["mentions"] / 10.0, 1.0)
            existing["confidence"] = round(max(0.0, min(0.4 * support + 0.3 * consensus + 0.2 * freq + 0.1 * 1.0, 1.0)), 4)
        else:
            entities[ent_id] = node.dict()
            
    save_graph()

def append_relations(relation_nodes: List[RelationNode]):
    """
    Incrementally inserts or reinforces RelationNodes.
    """
    load_graph()
    relations = _global_graph.setdefault("relations", {})
    now_str = datetime.utcnow().isoformat()
    
    for rel in relation_nodes:
        rel_id = rel.relation_id
        if rel_id in relations:
            # Reinforcement instead of overwrite
            existing = relations[rel_id]
            existing["confirmation_count"] += 1
            existing["weight"] += rel.confidence
            existing["evidence_ids"] = list(set(existing.get("evidence_ids", []) + rel.evidence_ids))
            existing["source_modalities"] = list(set(existing.get("source_modalities", []) + rel.source_modalities))
            existing["updated_at"] = now_str
            existing["last_confirmed"] = now_str
            
            # Recompute confidence
            support = min(len(existing["evidence_ids"]) / 5.0, 1.0) if existing["evidence_ids"] else 0.2
            conf_cnt = min(existing["confirmation_count"] / 5.0, 1.0)
            existing["confidence"] = round(max(0.0, min(0.5 * support + 0.3 * conf_cnt + 0.2 * 1.0, 1.0)), 4)
        else:
            relations[rel_id] = rel.dict()
            
    save_graph()

def append_temporal_event(event_node: TemporalNode):
    """
    Appends a new event timeline node.
    """
    load_graph()
    events = _global_graph.setdefault("temporal_events", [])
    events.append(event_node.dict())
    save_graph()

def save_communities(community_nodes: List[CommunityNode]):
    """
    Saves computed CommunityNodes.
    """
    load_graph()
    comms = _global_graph.setdefault("communities", {})
    comms.clear()
    for comm in community_nodes:
        comms[comm.community_id] = comm.dict()
    save_graph()

def clear_graph_store():
    """
    Resets the persistent Knowledge Graph file.
    """
    global _global_graph
    _global_graph = {
        "schema_version": 1,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "entities": {},
        "relations": {},
        "communities": {},
        "subgraphs": {},
        "temporal_events": []
    }
    save_graph()
