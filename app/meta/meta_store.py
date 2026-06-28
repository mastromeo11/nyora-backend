import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.meta.meta_models import (
    ToolLearningNode,
    PlannerPolicyNode,
    MetaReflectionNode,
    StrategyNode,
    PolicyReplayNode,
    ToolFailureNode,
    PolicyFailureNode,
    ReflectionFailureNode,
    PolicySummaryNode,
    PolicyArchiveNode,
    PolicySimilarityNode,
    OptimizationFailureNode,
    MetaArchiveNode
)
from app.config import META_SCHEMA_VERSION, ENABLE_POLICY_MIGRATIONS

META_MEMORY_FILE_PATH = os.path.abspath("storage/meta_memory.json")
_lock = threading.Lock()

_global_meta_store: Dict[str, Any] = {
    "schema_version": META_SCHEMA_VERSION,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "tool_learnings": {},
    "planner_policies": {},
    "meta_reflections": {},
    "strategies": {},
    "policy_replays": {},
    "tool_failures": {},
    "policy_failures": {},
    "reflection_failures": {},
    "optimization_failures": {},
    "policy_summaries": {},
    "policy_archives": {},
    "meta_archives": {},
    "policy_similarity_nodes": {}
}

_loaded = False

def load_meta_store() -> Dict[str, Any]:
    global _global_meta_store, _loaded
    with _lock:
        if not _loaded:
            os.makedirs(os.path.dirname(META_MEMORY_FILE_PATH), exist_ok=True)
            if os.path.exists(META_MEMORY_FILE_PATH):
                try:
                    with open(META_MEMORY_FILE_PATH, "r") as f:
                        data = json.load(f)
                        if ENABLE_POLICY_MIGRATIONS:
                            from app.meta.meta_migrations import run_meta_migrations
                            _global_meta_store = run_meta_migrations(data)
                        else:
                            _global_meta_store = data
                except Exception as e:
                    print(f"[META STORE] Error reading file: {e}. Using empty default memory.")
            else:
                _save_meta_store_nolock()
            _loaded = True
    return _global_meta_store

def save_meta_store():
    with _lock:
        _save_meta_store_nolock()

def _save_meta_store_nolock():
    global _global_meta_store
    os.makedirs(os.path.dirname(META_MEMORY_FILE_PATH), exist_ok=True)
    _global_meta_store["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = META_MEMORY_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_meta_store, f, indent=4)
        os.replace(temp_path, META_MEMORY_FILE_PATH)
    except Exception as e:
        print(f"[META STORE] Error performing atomic write: {e}")

# --- GETTERS ---

def get_tools() -> List[ToolLearningNode]:
    store = load_meta_store()
    return [ToolLearningNode(**d) for d in store.setdefault("tool_learnings", {}).values()]

def get_policies() -> List[PlannerPolicyNode]:
    store = load_meta_store()
    return [PlannerPolicyNode(**d) for d in store.setdefault("planner_policies", {}).values()]

def get_reflections() -> List[MetaReflectionNode]:
    store = load_meta_store()
    return [MetaReflectionNode(**d) for d in store.setdefault("meta_reflections", {}).values()]

def get_strategies() -> List[StrategyNode]:
    store = load_meta_store()
    return [StrategyNode(**d) for d in store.setdefault("strategies", {}).values()]

def get_replays() -> List[PolicyReplayNode]:
    store = load_meta_store()
    return [PolicyReplayNode(**d) for d in store.setdefault("policy_replays", {}).values()]

def get_tool_failures() -> List[ToolFailureNode]:
    store = load_meta_store()
    return [ToolFailureNode(**d) for d in store.setdefault("tool_failures", {}).values()]

def get_policy_failures() -> List[PolicyFailureNode]:
    store = load_meta_store()
    return [PolicyFailureNode(**d) for d in store.setdefault("policy_failures", {}).values()]

def get_reflection_failures() -> List[ReflectionFailureNode]:
    store = load_meta_store()
    return [ReflectionFailureNode(**d) for d in store.setdefault("reflection_failures", {}).values()]

def get_summaries() -> List[PolicySummaryNode]:
    store = load_meta_store()
    return [PolicySummaryNode(**d) for d in store.setdefault("policy_summaries", {}).values()]

def get_archives() -> List[PolicyArchiveNode]:
    store = load_meta_store()
    return [PolicyArchiveNode(**d) for d in store.setdefault("policy_archives", {}).values()]

def get_similarity_nodes() -> List[PolicySimilarityNode]:
    store = load_meta_store()
    return [PolicySimilarityNode(**d) for d in store.setdefault("policy_similarity_nodes", {}).values()]

def get_optimization_failures() -> List[OptimizationFailureNode]:
    store = load_meta_store()
    return [OptimizationFailureNode(**d) for d in store.setdefault("optimization_failures", {}).values()]

def get_meta_archives() -> List[MetaArchiveNode]:
    store = load_meta_store()
    return [MetaArchiveNode(**d) for d in store.setdefault("meta_archives", {}).values()]

# --- APPENDERS ---

def append_tool(node: ToolLearningNode):
    store = load_meta_store()
    store.setdefault("tool_learnings", {})[node.tool_id] = node.model_dump()
    save_meta_store()
    try:
        from app.meta.policy_cache import clear_all_policy_caches
        clear_all_policy_caches()
    except ImportError:
        pass

def append_policy(node: PlannerPolicyNode):
    store = load_meta_store()
    store.setdefault("planner_policies", {})[node.policy_id] = node.model_dump()
    save_meta_store()
    try:
        from app.meta.policy_cache import clear_all_policy_caches
        clear_all_policy_caches()
    except ImportError:
        pass

def append_reflection(node: MetaReflectionNode):
    store = load_meta_store()
    store.setdefault("meta_reflections", {})[node.reflection_id] = node.model_dump()
    save_meta_store()
    try:
        from app.meta.policy_cache import clear_all_policy_caches
        clear_all_policy_caches()
    except ImportError:
        pass

def append_strategy(node: StrategyNode):
    store = load_meta_store()
    store.setdefault("strategies", {})[node.strategy_id] = node.model_dump()
    save_meta_store()
    try:
        from app.meta.policy_cache import clear_all_policy_caches
        clear_all_policy_caches()
    except ImportError:
        pass

def append_replay(node: PolicyReplayNode):
    store = load_meta_store()
    store.setdefault("policy_replays", {})[node.replay_id] = node.model_dump()
    save_meta_store()

def append_tool_failure(node: ToolFailureNode):
    store = load_meta_store()
    store.setdefault("tool_failures", {})[node.failure_id] = node.model_dump()
    save_meta_store()

def append_policy_failure(node: PolicyFailureNode):
    store = load_meta_store()
    store.setdefault("policy_failures", {})[node.failure_id] = node.model_dump()
    save_meta_store()

def append_reflection_failure(node: ReflectionFailureNode):
    store = load_meta_store()
    store.setdefault("reflection_failures", {})[node.failure_id] = node.model_dump()
    save_meta_store()

def append_summary(node: PolicySummaryNode):
    store = load_meta_store()
    store.setdefault("policy_summaries", {})[node.summary_id] = node.model_dump()
    save_meta_store()

def append_archive(node: PolicyArchiveNode):
    store = load_meta_store()
    store.setdefault("policy_archives", {})[node.archive_id] = node.model_dump()
    save_meta_store()

def append_similarity_node(node: PolicySimilarityNode):
    store = load_meta_store()
    key = f"{node.source_policy}_{node.target_policy}"
    store.setdefault("policy_similarity_nodes", {})[key] = node.model_dump()
    save_meta_store()

def append_optimization_failure(node: OptimizationFailureNode):
    store = load_meta_store()
    store.setdefault("optimization_failures", {})[node.failure_id] = node.model_dump()
    save_meta_store()

def append_meta_archive(node: MetaArchiveNode):
    store = load_meta_store()
    store.setdefault("meta_archives", {})[node.archive_id] = node.model_dump()
    save_meta_store()

def clear_meta_store():
    global _global_meta_store, _loaded
    with _lock:
        _global_meta_store = {
            "schema_version": META_SCHEMA_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "tool_learnings": {},
            "planner_policies": {},
            "meta_reflections": {},
            "strategies": {},
            "policy_replays": {},
            "tool_failures": {},
            "policy_failures": {},
            "reflection_failures": {},
            "optimization_failures": {},
            "policy_summaries": {},
            "policy_archives": {},
            "meta_archives": {},
            "policy_similarity_nodes": {}
        }
        _save_meta_store_nolock()
        _loaded = True
