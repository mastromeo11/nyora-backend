import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.simulation.simulation_models import (
    WorldStateNode,
    HypothesisNode,
    ScenarioNode,
    CounterfactualNode,
    SimulationNode,
    PolicyNode,
    FailureForecastNode,
    FailureSimulationNode,
    ScenarioSummaryNode,
    PolicyFailureNode,
    SimulationArchiveNode
)
from app.simulation.world_model_migrations import run_world_model_migrations
from app.config import WORLD_MODEL_SCHEMA_VERSION, ENABLE_WORLD_MODEL_MIGRATIONS

WORLD_MODEL_FILE_PATH = os.path.abspath("storage/world_models.json")
_lock = threading.Lock()

_global_world_model: Dict[str, Any] = {
    "schema_version": WORLD_MODEL_SCHEMA_VERSION,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "world_states": {},
    "hypotheses": {},
    "scenarios": {},
    "counterfactuals": {},
    "simulations": {},
    "policies": {},
    "failure_forecasts": {},
    "failure_simulations": {},
    "scenario_summaries": {},
    "policy_failures": {},
    "simulation_archives": {}
}

_loaded = False

def load_world_model_store() -> Dict[str, Any]:
    global _global_world_model, _loaded
    with _lock:
        if not _loaded:
            os.makedirs(os.path.dirname(WORLD_MODEL_FILE_PATH), exist_ok=True)
            if os.path.exists(WORLD_MODEL_FILE_PATH):
                try:
                    with open(WORLD_MODEL_FILE_PATH, "r") as f:
                        data = json.load(f)
                        if ENABLE_WORLD_MODEL_MIGRATIONS:
                            _global_world_model = run_world_model_migrations(data)
                        else:
                            _global_world_model = data
                except Exception as e:
                    print(f"[WORLD MODEL STORE] Error reading file: {e}. Using empty default memory.")
            else:
                _save_world_model_store_nolock()
            _loaded = True
    return _global_world_model

def save_world_model_store():
    with _lock:
        _save_world_model_store_nolock()

def _save_world_model_store_nolock():
    global _global_world_model
    os.makedirs(os.path.dirname(WORLD_MODEL_FILE_PATH), exist_ok=True)
    _global_world_model["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = WORLD_MODEL_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_world_model, f, indent=4)
        os.replace(temp_path, WORLD_MODEL_FILE_PATH)
        
        # Invalidate caches
        from app.simulation.world_model_cache import clear_all_simulation_caches
        clear_all_simulation_caches()
    except Exception as e:
        print(f"[WORLD MODEL STORE] Error performing atomic write: {e}")

# --- GETTERS ---

def get_world_states() -> List[WorldStateNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("world_states", {}).values():
        nodes.append(WorldStateNode(**data))
    return nodes

def get_hypotheses() -> List[HypothesisNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("hypotheses", {}).values():
        nodes.append(HypothesisNode(**data))
    return nodes

def get_scenarios() -> List[ScenarioNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("scenarios", {}).values():
        nodes.append(ScenarioNode(**data))
    return nodes

def get_counterfactuals() -> List[CounterfactualNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("counterfactuals", {}).values():
        nodes.append(CounterfactualNode(**data))
    return nodes

def get_simulations() -> List[SimulationNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("simulations", {}).values():
        nodes.append(SimulationNode(**data))
    return nodes

def get_policies() -> List[PolicyNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("policies", {}).values():
        nodes.append(PolicyNode(**data))
    return nodes

def get_failure_forecasts() -> List[FailureForecastNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("failure_forecasts", {}).values():
        nodes.append(FailureForecastNode(**data))
    return nodes

def get_failure_simulations() -> List[FailureSimulationNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("failure_simulations", {}).values():
        nodes.append(FailureSimulationNode(**data))
    return nodes

def get_scenario_summaries() -> List[ScenarioSummaryNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("scenario_summaries", {}).values():
        nodes.append(ScenarioSummaryNode(**data))
    return nodes

def get_policy_failures() -> List[PolicyFailureNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("policy_failures", {}).values():
        nodes.append(PolicyFailureNode(**data))
    return nodes

def get_simulation_archives() -> List[SimulationArchiveNode]:
    mem = load_world_model_store()
    nodes = []
    for data in mem.get("simulation_archives", {}).values():
        nodes.append(SimulationArchiveNode(**data))
    return nodes

# --- SETTERS ---

def append_world_state(node: WorldStateNode):
    mem = load_world_model_store()
    mem.setdefault("world_states", {})[node.world_state_id] = node.model_dump()
    save_world_model_store()

def append_hypothesis(node: HypothesisNode):
    mem = load_world_model_store()
    mem.setdefault("hypotheses", {})[node.hypothesis_id] = node.model_dump()
    save_world_model_store()

def append_scenario(node: ScenarioNode):
    mem = load_world_model_store()
    mem.setdefault("scenarios", {})[node.scenario_id] = node.model_dump()
    save_world_model_store()

def append_counterfactual(node: CounterfactualNode):
    mem = load_world_model_store()
    mem.setdefault("counterfactuals", {})[node.counterfactual_id] = node.model_dump()
    save_world_model_store()

def append_simulation(node: SimulationNode):
    mem = load_world_model_store()
    mem.setdefault("simulations", {})[node.simulation_id] = node.model_dump()
    save_world_model_store()

def append_policy(node: PolicyNode):
    mem = load_world_model_store()
    mem.setdefault("policies", {})[node.policy_id] = node.model_dump()
    save_world_model_store()

def append_failure_forecast(node: FailureForecastNode):
    mem = load_world_model_store()
    mem.setdefault("failure_forecasts", {})[node.failure_forecast_id] = node.model_dump()
    save_world_model_store()

def append_failure_simulation(node: FailureSimulationNode):
    mem = load_world_model_store()
    mem.setdefault("failure_simulations", {})[node.failure_simulation_id] = node.model_dump()
    save_world_model_store()

def append_scenario_summary(node: ScenarioSummaryNode):
    mem = load_world_model_store()
    mem.setdefault("scenario_summaries", {})[node.summary_id] = node.model_dump()
    save_world_model_store()

def append_policy_failure(node: PolicyFailureNode):
    mem = load_world_model_store()
    mem.setdefault("policy_failures", {})[node.policy_id] = node.model_dump()
    save_world_model_store()

def append_simulation_archive(node: SimulationArchiveNode):
    mem = load_world_model_store()
    mem.setdefault("simulation_archives", {})[node.archive_id] = node.model_dump()
    save_world_model_store()

def clear_simulation_store():
    global _global_world_model, _loaded
    with _lock:
        _global_world_model = {
            "schema_version": WORLD_MODEL_SCHEMA_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "world_states": {},
            "hypotheses": {},
            "scenarios": {},
            "counterfactuals": {},
            "simulations": {},
            "policies": {},
            "failure_forecasts": {},
            "failure_simulations": {},
            "scenario_summaries": {},
            "policy_failures": {},
            "simulation_archives": {}
        }
        _save_world_model_store_nolock()
        _loaded = True
