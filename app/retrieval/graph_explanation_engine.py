import threading
from typing import List, Dict, Any, Optional
from app.retrieval.knowledge_models import EntityNode, RelationNode

# Global thread-safe store for the latest graph explanation diagnostics
_latest_graph_explanation = {
    "paths": [],
    "neighbors": [],
    "natural_summary": ""
}
_lock = threading.Lock()

def get_latest_graph_explanation() -> dict:
    """
    Returns the latest compiled graph explanation diagnostics.
    """
    with _lock:
        return dict(_latest_graph_explanation)

def compile_graph_explanation(paths: List[List[Any]], neighbors: List[Dict[str, Any]] = None) -> dict:
    """
    Compiles natural explanations for paths and neighbors, updating the global diagnostic state.
    
    Args:
        paths (List[List[Any]]): A list of paths, each being [EntityNode, RelationNode, EntityNode, ...].
        neighbors (List[Dict[str, Any]]): A list of direct neighbors returned by query_neighbors.
        
    Returns:
        dict: The compiled explanation diagnostic object.
    """
    global _latest_graph_explanation
    
    path_summaries = []
    for path in paths:
        if not path:
            continue
        # Format path elements naturally
        parts = []
        for idx, element in enumerate(path):
            if isinstance(element, EntityNode):
                parts.append(element.name)
            elif isinstance(element, RelationNode):
                # E.g. USES -> "uses", CONNECTS_TO -> "connects to"
                rel_desc = element.relation_type.replace("_", " ").lower()
                parts.append(f"which {rel_desc}")
        # Combine. E.g. "ChromaDB which uses FastAPI which connects to Ollama"
        path_str = " ".join(parts)
        # Clean up double "which" if any or format nicely
        path_str = path_str.replace(" which", ", which")
        path_summaries.append(path_str)

    neighbor_summaries = []
    if neighbors:
        for item in neighbors:
            neighbor = item["neighbor"]
            rel = item["relation"]
            direction = item["direction"]
            rel_desc = rel.relation_type.replace("_", " ").lower()
            
            if direction == "outgoing":
                neighbor_summaries.append(f"{rel.source_entity} {rel_desc} {neighbor.name}")
            else:
                neighbor_summaries.append(f"{neighbor.name} {rel_desc} {rel.target_entity}")

    # Build natural summary
    summary_parts = []
    if path_summaries:
        summary_parts.append("Discovered multi-hop relations in the Knowledge Graph: " + "; ".join(path_summaries) + ".")
    if neighbor_summaries:
        summary_parts.append("Direct entity connections: " + ", ".join(neighbor_summaries) + ".")
        
    natural_summary = " ".join(summary_parts) if summary_parts else "No relevant knowledge graph relations identified for this context."

    diag = {
        "paths": [", ".join([e.name if isinstance(e, EntityNode) else e.relation_type for e in p]) for p in paths],
        "neighbors": neighbor_summaries,
        "natural_summary": natural_summary
    }

    with _lock:
        _latest_graph_explanation = diag
        
    return diag
