from datetime import datetime
from app.config import EPISODIC_SCHEMA_VERSION

def run_episodic_migrations(data: dict) -> dict:
    """
    Checks the schema_version of the input dataset and automatically upgrades it to the current schema format.
    """
    current_version = data.get("schema_version", 0)
    
    if current_version < EPISODIC_SCHEMA_VERSION:
        print(f"[EPISODIC MIGRATION] Migrating database from version {current_version} to {EPISODIC_SCHEMA_VERSION}")
        
        # Initialize default structures if missing
        if "episodes" not in data:
            data["episodes"] = {}
        if "experiences" not in data:
            data["experiences"] = {}
        if "replays" not in data:
            data["replays"] = {}
        if "temporal_chains" not in data:
            data["temporal_chains"] = {}
        if "clusters" not in data:
            data["clusters"] = {}
        if "failure_replays" not in data:
            data["failure_replays"] = {}
        if "chain_summaries" not in data:
            data["chain_summaries"] = {}
            
        # Migrate old chains key if it was named "chains"
        if "chains" in data and "temporal_chains" not in data:
            data["temporal_chains"] = data.pop("chains")
            
        data["schema_version"] = EPISODIC_SCHEMA_VERSION
        data["updated_at"] = datetime.utcnow().isoformat()
        
    return data
