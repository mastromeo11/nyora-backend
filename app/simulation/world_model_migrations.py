from datetime import datetime
from app.config import WORLD_MODEL_SCHEMA_VERSION

def run_world_model_migrations(data: dict) -> dict:
    """
    Ensures that the loaded world models data conforms to the latest schema version.
    """
    current_version = data.get("schema_version", 0)
    if current_version < WORLD_MODEL_SCHEMA_VERSION:
        print(f"[WORLD MODEL MIGRATIONS] Upgrading database from version {current_version} to {WORLD_MODEL_SCHEMA_VERSION}")
        # Initialize fields if they don't exist
        for key in ["world_states", "hypotheses", "scenarios", "counterfactuals", "simulations", "policies", "failure_forecasts", "failure_simulations", "scenario_summaries", "policy_failures", "simulation_archives"]:
            if key not in data:
                data[key] = {}
        data["schema_version"] = WORLD_MODEL_SCHEMA_VERSION
        data["updated_at"] = datetime.utcnow().isoformat()
    return data
