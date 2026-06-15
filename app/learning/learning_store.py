import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.learning.learning_models import (
    PatternNode,
    CorrectionNode,
    FeedbackNode,
    LearningNode,
    QueryClusterNode,
    FailurePatternNode
)
from app.learning.learning_migrations import run_learning_migrations
from app.config import LEARNING_SCHEMA_VERSION, ENABLE_LEARNING_MIGRATIONS

LEARNING_FILE_PATH = os.path.abspath("storage/learning_memory.json")
_lock = threading.Lock()

# In-memory learning database representation
_global_learning_memory: Dict[str, Any] = {
    "schema_version": 1,
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "patterns": {},
    "corrections": {},
    "feedback": {},
    "clusters": {},
    "learning_nodes": {},
    "failure_patterns": {}
}

def load_learning_store() -> Dict[str, Any]:
    """
    Loads and optionally migrates the persistent self-learning memory file.
    """
    global _global_learning_memory
    with _lock:
        os.makedirs(os.path.dirname(LEARNING_FILE_PATH), exist_ok=True)
        if os.path.exists(LEARNING_FILE_PATH):
            try:
                with open(LEARNING_FILE_PATH, "r") as f:
                    data = json.load(f)
                    if ENABLE_LEARNING_MIGRATIONS:
                        _global_learning_memory = run_learning_migrations(data)
                    else:
                        _global_learning_memory = data
            except Exception as e:
                print(f"[LEARNING STORE] Error reading file: {e}. Using empty default memory.")
        else:
            # First time initialization
            _save_learning_store_nolock()
            
    return _global_learning_memory

def save_learning_store():
    """
    Saves the in-memory learning database to disk using an atomic write.
    """
    with _lock:
        _save_learning_store_nolock()

def _save_learning_store_nolock():
    global _global_learning_memory
    os.makedirs(os.path.dirname(LEARNING_FILE_PATH), exist_ok=True)
    _global_learning_memory["updated_at"] = datetime.utcnow().isoformat()
    try:
        temp_path = LEARNING_FILE_PATH + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(_global_learning_memory, f, indent=4)
        os.replace(temp_path, LEARNING_FILE_PATH)
        # Invalidate learning caches whenever a write occurs
        from app.learning.learning_cache import clear_all_learning_caches
        clear_all_learning_caches()
    except Exception as e:
        print(f"[LEARNING STORE] Error performing atomic write: {e}")

# --- API ACCESSORS ---

def get_patterns() -> List[PatternNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("patterns", {}).values():
        nodes.append(PatternNode(**data))
    return nodes

def get_corrections() -> List[CorrectionNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("corrections", {}).values():
        nodes.append(CorrectionNode(**data))
    return nodes

def get_feedback() -> List[FeedbackNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("feedback", {}).values():
        nodes.append(FeedbackNode(**data))
    return nodes

def get_learnings() -> List[LearningNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("learning_nodes", {}).values():
        nodes.append(LearningNode(**data))
    return nodes

def get_failure_patterns() -> List[FailurePatternNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("failure_patterns", {}).values():
        nodes.append(FailurePatternNode(**data))
    return nodes

def get_clusters() -> List[QueryClusterNode]:
    mem = load_learning_store()
    nodes = []
    for data in mem.get("clusters", {}).values():
        nodes.append(QueryClusterNode(**data))
    return nodes

# --- ATOMIC APPEND MODIFIERS ---

def append_pattern(node: PatternNode):
    mem = load_learning_store()
    patterns = mem.setdefault("patterns", {})
    patterns[node.pattern_id] = node.dict()
    save_learning_store()

def append_correction(node: CorrectionNode):
    mem = load_learning_store()
    corrections = mem.setdefault("corrections", {})
    corrections[node.correction_id] = node.dict()
    save_learning_store()

def append_feedback(node: FeedbackNode):
    mem = load_learning_store()
    feedback = mem.setdefault("feedback", {})
    feedback[node.feedback_id] = node.dict()
    save_learning_store()

def append_learning(node: LearningNode):
    mem = load_learning_store()
    learnings = mem.setdefault("learning_nodes", {})
    learnings[node.learning_id] = node.dict()
    save_learning_store()

def append_failure_pattern(node: FailurePatternNode):
    mem = load_learning_store()
    failures = mem.setdefault("failure_patterns", {})
    failures[node.failure_pattern_id] = node.dict()
    save_learning_store()

def save_clusters(cluster_nodes: List[QueryClusterNode]):
    mem = load_learning_store()
    clusters = mem.setdefault("clusters", {})
    clusters.clear()
    for cluster in cluster_nodes:
        clusters[cluster.cluster_id] = cluster.dict()
    save_learning_store()

def clear_learning_store():
    """
    Resets the persistent Continual Learning database file.
    """
    global _global_learning_memory
    with _lock:
        _global_learning_memory = {
            "schema_version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "patterns": {},
            "corrections": {},
            "feedback": {},
            "clusters": {},
            "learning_nodes": {},
            "failure_patterns": {}
        }
        _save_learning_store_nolock()
