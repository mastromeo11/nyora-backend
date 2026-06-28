import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.episodic.episodic_models import (
    EpisodeNode,
    ExperienceNode,
    ReplayNode,
    TemporalChainNode,
    MemoryClusterNode,
    FailureReplayNode,
    ChainSummaryNode
)
from app.episodic.episodic_migrations import run_episodic_migrations
from app.config import EPISODIC_SCHEMA_VERSION, ENABLE_EPISODIC_MIGRATIONS

EPISODIC_FILE_PATH = os.path.abspath("storage/episodic_memory.json")
_lock = threading.Lock()

_global_episodic_memory: Dict[str, Any] = {
    "schema_version": EPISODIC_SCHEMA_VERSION,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "episodes": {},
    "experiences": {},
    "replays": {},
    "temporal_chains": {},
    "clusters": {},
    "failure_replays": {},
    "chain_summaries": {}
}

_loaded = False

def load_episodic_store() -> Dict[str, Any]:
    global _global_episodic_memory, _loaded
    with _lock:
        if not _loaded:
            os.makedirs(os.path.dirname(EPISODIC_FILE_PATH), exist_ok=True)
            if os.path.exists(EPISODIC_FILE_PATH):
                try:
                    with open(EPISODIC_FILE_PATH, "r") as f:
                        data = json.load(f)
                        if ENABLE_EPISODIC_MIGRATIONS:
                            _global_episodic_memory = run_episodic_migrations(data)
                        else:
                            _global_episodic_memory = data
                except Exception as e:
                    print(f"[EPISODIC STORE] Error reading file: {e}. Using empty default memory.")
            else:
                _save_episodic_store_nolock()
            _loaded = True
    return _global_episodic_memory

def save_episodic_store():
    with _lock:
        _save_episodic_store_nolock()

def _save_episodic_store_nolock():
    global _global_episodic_memory
    os.makedirs(os.path.dirname(EPISODIC_FILE_PATH), exist_ok=True)
    _global_episodic_memory["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = EPISODIC_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_episodic_memory, f, indent=4)
        os.replace(temp_path, EPISODIC_FILE_PATH)
        
        # Invalidate caches
        from app.episodic.episodic_cache import clear_all_episodic_caches
        clear_all_episodic_caches()
    except Exception as e:
        print(f"[EPISODIC STORE] Error performing atomic write: {e}")

# --- GETTERS ---

def get_episodes() -> List[EpisodeNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("episodes", {}).values():
        nodes.append(EpisodeNode(**data))
    return nodes

def get_experiences() -> List[ExperienceNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("experiences", {}).values():
        nodes.append(ExperienceNode(**data))
    return nodes

def get_replays() -> List[ReplayNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("replays", {}).values():
        nodes.append(ReplayNode(**data))
    return nodes

def get_chains() -> List[TemporalChainNode]:
    mem = load_episodic_store()
    nodes = []
    # Backward compatibility checks
    chains_data = mem.get("temporal_chains", mem.get("chains", {}))
    for data in chains_data.values():
        nodes.append(TemporalChainNode(**data))
    return nodes

def get_clusters() -> List[MemoryClusterNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("clusters", {}).values():
        nodes.append(MemoryClusterNode(**data))
    return nodes

def get_failure_replays() -> List[FailureReplayNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("failure_replays", {}).values():
        nodes.append(FailureReplayNode(**data))
    return nodes

def get_chain_summaries() -> List[ChainSummaryNode]:
    mem = load_episodic_store()
    nodes = []
    for data in mem.get("chain_summaries", {}).values():
        nodes.append(ChainSummaryNode(**data))
    return nodes

# --- SETTERS ---

def append_episode(node: EpisodeNode):
    mem = load_episodic_store()
    episodes = mem.setdefault("episodes", {})
    episodes[node.episode_id] = node.model_dump()
    save_episodic_store()

def append_experience(node: ExperienceNode):
    mem = load_episodic_store()
    experiences = mem.setdefault("experiences", {})
    experiences[node.experience_id] = node.model_dump()
    save_episodic_store()

def append_replay(node: ReplayNode):
    mem = load_episodic_store()
    replays = mem.setdefault("replays", {})
    replays[node.replay_id] = node.model_dump()
    save_episodic_store()

def append_chain(node: TemporalChainNode):
    mem = load_episodic_store()
    chains = mem.setdefault("temporal_chains", {})
    chains[node.chain_id] = node.model_dump()
    save_episodic_store()

def append_cluster(node: MemoryClusterNode):
    mem = load_episodic_store()
    clusters = mem.setdefault("clusters", {})
    clusters[node.cluster_id] = node.model_dump()
    save_episodic_store()

def save_clusters(cluster_nodes: List[MemoryClusterNode]):
    mem = load_episodic_store()
    clusters = mem.setdefault("clusters", {})
    clusters.clear()
    for cluster in cluster_nodes:
        clusters[cluster.cluster_id] = cluster.model_dump()
    save_episodic_store()

def append_failure_replay(node: FailureReplayNode):
    mem = load_episodic_store()
    failures = mem.setdefault("failure_replays", {})
    failures[node.failure_replay_id] = node.model_dump()
    save_episodic_store()

def append_chain_summary(node: ChainSummaryNode):
    mem = load_episodic_store()
    summaries = mem.setdefault("chain_summaries", {})
    summaries[node.chain_summary_id] = node.model_dump()
    save_episodic_store()

def clear_episodic_store():
    global _global_episodic_memory, _loaded
    with _lock:
        _global_episodic_memory = {
            "schema_version": EPISODIC_SCHEMA_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "episodes": {},
            "experiences": {},
            "replays": {},
            "temporal_chains": {},
            "clusters": {},
            "failure_replays": {},
            "chain_summaries": {}
        }
        _save_episodic_store_nolock()
        _loaded = True
