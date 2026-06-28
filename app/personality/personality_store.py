import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.personality.personality_models import (
    HumanPreferenceNode,
    NegativePreferenceNode,
    UserStyleNode,
    AdaptivePersonalityNode,
    InteractionMemoryNode,
    RecommendationMemoryNode,
    PersonalityReplayNode,
    PersonalityFailureNode,
    AbandonedInteractionNode,
    RecommendationFailureNode,
    PersonalitySummaryNode,
    PersonalityArchiveNode,
    PersonalitySimilarityNode,
    InteractionSummaryNode
)
from app.config import PERSONALITY_SCHEMA_VERSION, ENABLE_PERSONALITY_MIGRATIONS

PERSONALITY_MEMORY_FILE_PATH = os.path.abspath("storage/personality_memory.json")
_lock = threading.Lock()

_global_personality_store: Dict[str, Any] = {
    "schema_version": PERSONALITY_SCHEMA_VERSION,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "preferences": {},
    "negative_preferences": {},
    "user_styles": {},
    "adaptive_personalities": {},
    "interaction_memories": {},
    "recommendation_memories": {},
    "personality_replays": {},
    "personality_failures": {},
    "abandoned_interactions": {},
    "recommendation_failures": {},
    "personality_summaries": {},
    "interaction_summaries": {},
    "personality_archives": {},
    "personality_similarity_nodes": {}
}

_loaded = False

def load_personality_store() -> Dict[str, Any]:
    global _global_personality_store, _loaded
    with _lock:
        if not _loaded:
            os.makedirs(os.path.dirname(PERSONALITY_MEMORY_FILE_PATH), exist_ok=True)
            if os.path.exists(PERSONALITY_MEMORY_FILE_PATH):
                try:
                    with open(PERSONALITY_MEMORY_FILE_PATH, "r") as f:
                        data = json.load(f)
                        if ENABLE_PERSONALITY_MIGRATIONS:
                            from app.personality.personality_migrations import run_personality_migrations
                            _global_personality_store = run_personality_migrations(data)
                        else:
                            _global_personality_store = data
                except Exception as e:
                    print(f"[PERSONALITY STORE] Error reading file: {e}. Using empty default memory.")
            else:
                _save_personality_store_nolock()
            _loaded = True
    return _global_personality_store

def save_personality_store():
    with _lock:
        _save_personality_store_nolock()

def _save_personality_store_nolock():
    global _global_personality_store
    os.makedirs(os.path.dirname(PERSONALITY_MEMORY_FILE_PATH), exist_ok=True)
    _global_personality_store["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = PERSONALITY_MEMORY_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_personality_store, f, indent=4)
        os.replace(temp_path, PERSONALITY_MEMORY_FILE_PATH)
    except Exception as e:
        print(f"[PERSONALITY STORE] Error performing atomic write: {e}")

# --- GETTERS ---

def get_preferences() -> List[HumanPreferenceNode]:
    store = load_personality_store()
    return [HumanPreferenceNode(**d) for d in store.setdefault("preferences", {}).values()]

def get_negative_preferences() -> List[NegativePreferenceNode]:
    store = load_personality_store()
    return [NegativePreferenceNode(**d) for d in store.setdefault("negative_preferences", {}).values()]

def get_user_styles() -> List[UserStyleNode]:
    store = load_personality_store()
    return [UserStyleNode(**d) for d in store.setdefault("user_styles", {}).values()]

def get_adaptive_personalities() -> List[AdaptivePersonalityNode]:
    store = load_personality_store()
    return [AdaptivePersonalityNode(**d) for d in store.setdefault("adaptive_personalities", {}).values()]

def get_interaction_memories() -> List[InteractionMemoryNode]:
    store = load_personality_store()
    return [InteractionMemoryNode(**d) for d in store.setdefault("interaction_memories", {}).values()]

def get_recommendation_memories() -> List[RecommendationMemoryNode]:
    store = load_personality_store()
    return [RecommendationMemoryNode(**d) for d in store.setdefault("recommendation_memories", {}).values()]

def get_personality_replays() -> List[PersonalityReplayNode]:
    store = load_personality_store()
    return [PersonalityReplayNode(**d) for d in store.setdefault("personality_replays", {}).values()]

def get_personality_failures() -> List[PersonalityFailureNode]:
    store = load_personality_store()
    return [PersonalityFailureNode(**d) for d in store.setdefault("personality_failures", {}).values()]

def get_abandoned_interactions() -> List[AbandonedInteractionNode]:
    store = load_personality_store()
    return [AbandonedInteractionNode(**d) for d in store.setdefault("abandoned_interactions", {}).values()]

def get_recommendation_failures() -> List[RecommendationFailureNode]:
    store = load_personality_store()
    return [RecommendationFailureNode(**d) for d in store.setdefault("recommendation_failures", {}).values()]

def get_personality_summaries() -> List[PersonalitySummaryNode]:
    store = load_personality_store()
    return [PersonalitySummaryNode(**d) for d in store.setdefault("personality_summaries", {}).values()]

def get_personality_archives() -> List[PersonalityArchiveNode]:
    store = load_personality_store()
    return [PersonalityArchiveNode(**d) for d in store.setdefault("personality_archives", {}).values()]

def get_personality_similarity_nodes() -> List[PersonalitySimilarityNode]:
    store = load_personality_store()
    return [PersonalitySimilarityNode(**d) for d in store.setdefault("personality_similarity_nodes", {}).values()]

def get_interaction_summaries() -> List[InteractionSummaryNode]:
    store = load_personality_store()
    return [InteractionSummaryNode(**d) for d in store.setdefault("interaction_summaries", {}).values()]

# --- APPENDERS ---

def append_preference(node: HumanPreferenceNode):
    store = load_personality_store()
    store.setdefault("preferences", {})[node.preference_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_negative_preference(node: NegativePreferenceNode):
    store = load_personality_store()
    store.setdefault("negative_preferences", {})[node.preference_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_style(node: UserStyleNode):
    store = load_personality_store()
    store.setdefault("user_styles", {})[node.style_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_personality(node: AdaptivePersonalityNode):
    store = load_personality_store()
    store.setdefault("adaptive_personalities", {})[node.personality_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_interaction(node: InteractionMemoryNode):
    store = load_personality_store()
    store.setdefault("interaction_memories", {})[node.interaction_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_recommendation(node: RecommendationMemoryNode):
    store = load_personality_store()
    store.setdefault("recommendation_memories", {})[node.recommendation_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_personality_replay(node: PersonalityReplayNode):
    store = load_personality_store()
    store.setdefault("personality_replays", {})[node.replay_id] = node.model_dump()
    save_personality_store()

def append_personality_failure(node: PersonalityFailureNode):
    store = load_personality_store()
    store.setdefault("personality_failures", {})[node.failure_id] = node.model_dump()
    save_personality_store()

def append_abandoned_interaction(node: AbandonedInteractionNode):
    store = load_personality_store()
    store.setdefault("abandoned_interactions", {})[node.interaction_id] = node.model_dump()
    save_personality_store()

def append_recommendation_failure(node: RecommendationFailureNode):
    store = load_personality_store()
    store.setdefault("recommendation_failures", {})[node.failure_id] = node.model_dump()
    save_personality_store()

def append_personality_summary(node: PersonalitySummaryNode):
    store = load_personality_store()
    store.setdefault("personality_summaries", {})[node.summary_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_personality_archive(node: PersonalityArchiveNode):
    store = load_personality_store()
    store.setdefault("personality_archives", {})[node.archive_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def append_personality_similarity_node(node: PersonalitySimilarityNode):
    store = load_personality_store()
    key = f"{node.source_personality}_{node.target_personality}"
    store.setdefault("personality_similarity_nodes", {})[key] = node.model_dump()
    save_personality_store()

def append_interaction_summary(node: InteractionSummaryNode):
    store = load_personality_store()
    store.setdefault("interaction_summaries", {})[node.summary_id] = node.model_dump()
    save_personality_store()
    try:
        from app.personality.personality_cache import clear_all_personality_caches
        clear_all_personality_caches()
    except ImportError:
        pass

def clear_personality_store():
    global _global_personality_store, _loaded
    with _lock:
        _global_personality_store = {
            "schema_version": PERSONALITY_SCHEMA_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "preferences": {},
            "negative_preferences": {},
            "user_styles": {},
            "adaptive_personalities": {},
            "interaction_memories": {},
            "recommendation_memories": {},
            "personality_replays": {},
            "personality_failures": {},
            "abandoned_interactions": {},
            "recommendation_failures": {},
            "personality_summaries": {},
            "interaction_summaries": {},
            "personality_archives": {},
            "personality_similarity_nodes": {}
        }
        _save_personality_store_nolock()
        _loaded = True
