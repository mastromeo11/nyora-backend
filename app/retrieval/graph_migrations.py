import os
from datetime import datetime
from typing import Dict, Any

CURRENT_SCHEMA_VERSION = 1

def run_migrations(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks schema_version in graph_data and migrates it to CURRENT_SCHEMA_VERSION.
    """
    version = graph_data.get("schema_version", 0)
    
    if version == CURRENT_SCHEMA_VERSION:
        return graph_data
        
    print(f"[GRAPH MIGRATION] Migrating graph schema from v{version} to v{CURRENT_SCHEMA_VERSION}")
    
    now_str = datetime.utcnow().isoformat()
    
    # Migration from v0 to v1
    if version < 1:
        # Initialize standard fields
        if "entities" not in graph_data:
            graph_data["entities"] = {}
        if "relations" not in graph_data:
            graph_data["relations"] = {}
        if "communities" not in graph_data:
            graph_data["communities"] = {}
        if "subgraphs" not in graph_data:
            graph_data["subgraphs"] = {}
            
        graph_data["created_at"] = graph_data.get("created_at", now_str)
        graph_data["updated_at"] = now_str
        graph_data["schema_version"] = 1
        
    # Future version migrations can be chained here (e.g. if version < 2: ...)
    
    return graph_data
