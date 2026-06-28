from datetime import datetime
from app.config import META_SCHEMA_VERSION

def run_meta_migrations(data: dict) -> dict:
    """
    Ensures that the loaded meta memory data conforms to the latest schema version.
    """
    current_version = data.get("schema_version", 0)
    if current_version < META_SCHEMA_VERSION:
        print(f"[META MIGRATIONS] Upgrading database from version {current_version} to {META_SCHEMA_VERSION}")
        # Initialize fields if they don't exist
        keys = [
            "tool_learnings", "planner_policies", "meta_reflections", "strategies",
            "policy_replays", "tool_failures", "policy_failures", "reflection_failures",
            "policy_summaries", "policy_archives", "policy_similarity_nodes"
        ]
        for key in keys:
            if key not in data:
                data[key] = {}
        data["schema_version"] = META_SCHEMA_VERSION
        data["updated_at"] = datetime.utcnow().isoformat()
    return data
