from datetime import datetime
from typing import Dict, Any
from app.config import LEARNING_SCHEMA_VERSION

def run_learning_migrations(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks schema_version in learning memory data and migrates it to LEARNING_SCHEMA_VERSION.
    """
    version = data.get("schema_version", 0)
    
    if version == LEARNING_SCHEMA_VERSION:
        return data
        
    print(f"[LEARNING MIGRATION] Migrating learning schema from v{version} to v{LEARNING_SCHEMA_VERSION}")
    
    now_str = datetime.utcnow().isoformat()
    
    # Migration from v0 (or unversioned) to v1
    if version < 1:
        if "patterns" not in data:
            data["patterns"] = {}
        if "corrections" not in data:
            data["corrections"] = {}
        if "feedback" not in data:
            data["feedback"] = {}
        if "clusters" not in data:
            data["clusters"] = {}
        if "learning_nodes" not in data:
            data["learning_nodes"] = {}
        if "failure_patterns" not in data:
            data["failure_patterns"] = {}
            
        data["created_at"] = data.get("created_at", now_str)
        data["updated_at"] = now_str
        data["schema_version"] = 1
        
    # Future version migrations can be chained here (e.g. if version < 2: ...)
    
    return data
