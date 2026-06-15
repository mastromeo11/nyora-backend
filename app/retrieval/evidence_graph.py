from app.retrieval.evidence_models import EvidenceNode

# List of key entities to construct semantic linking edges
KEY_ENTITIES = [
    "chromadb", "fastapi", "ollama", "llama3.1", "clip", 
    "whisper", "vector", "embedding", "sustainable", "city", 
    "meeting", "alert", "error", "dashboard", "nodes", 
    "flowchart", "table", "investment"
]

def extract_entities(content: str) -> set[str]:
    """
    Extracts matches from the pre-defined KEY_ENTITIES set in lowercase.
    """
    found = set()
    c_lower = content.lower()
    for ent in KEY_ENTITIES:
        if ent in c_lower:
            found.add(ent)
    return found

from app.retrieval.entity_alias_map import get_node_entities

def build_evidence_graph(evidence_list: list[EvidenceNode]) -> dict:
    """
    Builds an Entity-Centric Evidence Graph.
    - Represents entities as nodes of type 'entity'.
    - Represents evidence files/nodes as nodes of type 'evidence'.
    - Links entities to other co-occurring entities ('entity_to_entity').
    - Links evidence nodes beneath their matching entities ('evidence_to_entity').
    """
    nodes = []
    edges = []
    
    # Collect all entities mentioned across all evidence nodes
    entities_present = set()
    for node in evidence_list:
        node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
        entities_present = entities_present.union(node_ents)
        
    # 1. Create Entity Nodes
    for ent in sorted(list(entities_present)):
        nodes.append({
            "id": f"entity_{ent}",
            "label": ent.upper(),
            "type": "entity"
        })
        
    # 2. Create Evidence Nodes
    for node in evidence_list:
        nodes.append({
            "id": node.evidence_id,
            "label": node.source,
            "type": "evidence",
            "modality": node.modality,
            "content": node.content,
            "score": node.retrieval_score
        })
        
    # 3. Create Entity-to-Entity edges
    # We link entities if they co-occur in the same evidence node content
    co_occurrences = set()
    for node in evidence_list:
        node_ents = list(get_node_entities(node.content).union(get_node_entities(node.source)))
        for i in range(len(node_ents)):
            for j in range(i + 1, len(node_ents)):
                ent_a, ent_b = sorted([node_ents[i], node_ents[j]])
                co_occurrences.add((ent_a, ent_b))
                
    for ent_a, ent_b in sorted(list(co_occurrences)):
        edges.append({
            "source": f"entity_{ent_a}",
            "target": f"entity_{ent_b}",
            "type": "entity_to_entity"
        })
        
    # 4. Create Evidence-to-Entity edges (connect evidence nodes beneath entities)
    for node in evidence_list:
        node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
        for ent in node_ents:
            edges.append({
                "source": node.evidence_id,
                "target": f"entity_{ent}",
                "type": "evidence_to_entity"
            })
            
    return {
        "nodes": nodes,
        "edges": edges
    }
