import os
import json
from typing import Dict, Any, List

CACHE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "storage/memory_cache.json"))

def _load_raw_cache() -> dict:
    if not os.path.exists(CACHE_PATH):
        return {"sessions": {}, "global_preferences": {}}
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading memory cache file: {e}")
        return {"sessions": {}, "global_preferences": {}}

def _save_raw_cache(data: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    try:
        temp_path = CACHE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, CACHE_PATH)
    except Exception as e:
        print(f"Error saving memory cache file: {e}")

def get_session_cache(session_id: str) -> dict:
    cache = _load_raw_cache()
    sessions = cache.setdefault("sessions", {})
    session_data = sessions.setdefault(session_id, {
        "active_entities": [],
        "current_entity_focus": None,
        "previous_entity_focus": None,
        "conversation_topic": None,
        "entity_memories": {},
        "preference_memory": {},
        "summaries": []
    })
    return session_data

def save_session_cache(session_id: str, session_data: dict):
    cache = _load_raw_cache()
    cache.setdefault("sessions", {})[session_id] = session_data
    _save_raw_cache(cache)

def get_global_preferences() -> dict:
    cache = _load_raw_cache()
    return cache.setdefault("global_preferences", {})

def save_global_preferences(prefs: dict):
    cache = _load_raw_cache()
    cache["global_preferences"] = prefs
    _save_raw_cache(cache)

def clear_all_caches():
    _save_raw_cache({"sessions": {}, "global_preferences": {}})
