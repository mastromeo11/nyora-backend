from datetime import datetime
from app.config import PERSONALITY_SCHEMA_VERSION

def run_personality_migrations(data: dict) -> dict:
    """
    Executes incremental database migrations to upgrade schema layout.
    """
    current_version = data.get("schema_version", 0)
    if current_version >= PERSONALITY_SCHEMA_VERSION:
        return data

    print(f"[PERSONALITY MIGRATIONS] Upgrading database from version {current_version} to {PERSONALITY_SCHEMA_VERSION}")

    # Migrate from version 0 to 1
    if current_version == 0:
        data["schema_version"] = 1
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Ensure all collections exist
        collections = [
            "preferences", "negative_preferences", "user_styles", "adaptive_personalities",
            "interaction_memories", "recommendation_memories", "personality_replays",
            "personality_failures", "abandoned_interactions", "recommendation_failures",
            "personality_summaries", "interaction_summaries", "personality_archives",
            "personality_similarity_nodes"
        ]
        for c in collections:
            if c not in data:
                data[c] = {}

    return data
