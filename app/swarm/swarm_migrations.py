from datetime import datetime
from typing import Dict, Any
from app.config import SWARM_SCHEMA_VERSION

def run_swarm_migrations(data: Dict[str, Any]) -> Dict[str, Any]:
    version = data.get("schema_version", 0)
    
    if version == SWARM_SCHEMA_VERSION:
        return data
        
    print(f"[SWARM MIGRATION] Migrating schema from v{version} to v{SWARM_SCHEMA_VERSION}")
    now_str = datetime.utcnow().isoformat()
    
    if version < 1:
        if "agents" not in data:
            data["agents"] = {}
        if "messages" not in data:
            data["messages"] = []
        if "delegations" not in data:
            data["delegations"] = []
        if "collaborations" not in data:
            data["collaborations"] = []
        if "consensus_nodes" not in data:
            data["consensus_nodes"] = []
        if "shared_memory" not in data:
            data["shared_memory"] = {}
            
        data["created_at"] = data.get("created_at", now_str)
        data["updated_at"] = now_str
        data["schema_version"] = 1
        
    return data
