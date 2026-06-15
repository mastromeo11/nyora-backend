import os
import json
import threading
from datetime import datetime
from typing import Dict, Any

SWARM_HISTORY_FILE = os.path.abspath("storage/swarm_history.json")
_lock = threading.Lock()

_global_swarm_store: Dict[str, Any] = {
    "schema_version": 1,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "agents": {},
    "messages": [],
    "delegations": [],
    "collaborations": [],
    "consensus_nodes": [],
    "shared_memory": {}
}

def load_swarm_store() -> Dict[str, Any]:
    global _global_swarm_store
    with _lock:
        os.makedirs(os.path.dirname(SWARM_HISTORY_FILE), exist_ok=True)
        if os.path.exists(SWARM_HISTORY_FILE):
            try:
                with open(SWARM_HISTORY_FILE, "r") as f:
                    data = json.load(f)
                    from app.swarm.swarm_migrations import run_swarm_migrations
                    _global_swarm_store = run_swarm_migrations(data)
            except Exception as e:
                print(f"[SWARM STORE] Error reading store: {e}")
        else:
            _save_swarm_store_nolock()
    return _global_swarm_store

def save_swarm_store():
    with _lock:
        _save_swarm_store_nolock()

def _save_swarm_store_nolock():
    global _global_swarm_store
    os.makedirs(os.path.dirname(SWARM_HISTORY_FILE), exist_ok=True)
    _global_swarm_store["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = SWARM_HISTORY_FILE + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_swarm_store, f, indent=4)
        os.replace(temp_path, SWARM_HISTORY_FILE)
    except Exception as e:
        print(f"[SWARM STORE] Error performing atomic write: {e}")

def append_agent(agent_data: Dict[str, Any]):
    store = load_swarm_store()
    agents = store.setdefault("agents", {})
    agents[agent_data["agent_id"]] = agent_data
    save_swarm_store()

def append_message(msg_data: Dict[str, Any]):
    store = load_swarm_store()
    msgs = store.setdefault("messages", [])
    msgs.append(msg_data)
    save_swarm_store()

def append_consensus(consensus_data: Dict[str, Any]):
    store = load_swarm_store()
    nodes = store.setdefault("consensus_nodes", [])
    nodes.append(consensus_data)
    save_swarm_store()

def append_collaboration(collab_data: Dict[str, Any]):
    store = load_swarm_store()
    collabs = store.setdefault("collaborations", [])
    collabs.append(collab_data)
    save_swarm_store()

def clear_swarm_store():
    global _global_swarm_store
    with _lock:
        _global_swarm_store = {
            "schema_version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "agents": {},
            "messages": [],
            "delegations": [],
            "collaborations": [],
            "consensus_nodes": [],
            "shared_memory": {}
        }
        _save_swarm_store_nolock()
