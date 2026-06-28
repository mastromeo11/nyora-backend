import threading
from datetime import datetime, timedelta

from app.config import (
    ENABLE_PERSONALITY_PRUNER,
    PERSONALITY_PRUNE_INTERVAL
)
from app.personality.personality_store import load_personality_store, save_personality_store
from app.personality.personality_cache import clear_all_personality_caches

_query_counter = 0
_counter_lock = threading.Lock()

def increment_query_counter():
    """
    Increments the global query counter and triggers pruning if the interval is reached.
    """
    global _query_counter
    if not ENABLE_PERSONALITY_PRUNER:
        return

    with _counter_lock:
        _query_counter += 1
        should_prune = (_query_counter % PERSONALITY_PRUNE_INTERVAL == 0)

    if should_prune:
        prune_personality_store()

def prune_personality_store():
    """
    Removes low-confidence preference/style nodes and isolated or stale failure trees.
    """
    store = load_personality_store()
    modified = False

    # Define confidence threshold for pruning
    MIN_CONFIDENCE = 0.05

    # 1. Prune Human Preferences
    preferences = store.setdefault("preferences", {})
    to_remove_prefs = [k for k, v in preferences.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_prefs:
        preferences.pop(k)
        modified = True

    # 2. Prune Negative Preferences
    neg_preferences = store.setdefault("negative_preferences", {})
    to_remove_neg = [k for k, v in neg_preferences.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_neg:
        neg_preferences.pop(k)
        modified = True

    # 3. Prune User Styles
    user_styles = store.setdefault("user_styles", {})
    to_remove_styles = [k for k, v in user_styles.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_styles:
        user_styles.pop(k)
        modified = True

    # 4. Prune Adaptive Personalities
    adaptive_personalities = store.setdefault("adaptive_personalities", {})
    to_remove_pers = [k for k, v in adaptive_personalities.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_pers:
        adaptive_personalities.pop(k)
        modified = True

    # 5. Prune Interaction Memories
    interaction_memories = store.setdefault("interaction_memories", {})
    to_remove_int = [k for k, v in interaction_memories.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_int:
        interaction_memories.pop(k)
        modified = True

    # 6. Prune Recommendation Memories
    recommendation_memories = store.setdefault("recommendation_memories", {})
    to_remove_rec = [k for k, v in recommendation_memories.items() if v.get("confidence", 1.0) < MIN_CONFIDENCE]
    for k in to_remove_rec:
        recommendation_memories.pop(k)
        modified = True

    # 7. Prune Stale Failures (e.g., older than 7 days)
    # Failures include: personality_failures, abandoned_interactions, recommendation_failures
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    failures = store.setdefault("personality_failures", {})
    to_remove_fail = [k for k, v in failures.items() if v.get("timestamp", "") < seven_days_ago]
    for k in to_remove_fail:
        failures.pop(k)
        modified = True

    abandoned = store.setdefault("abandoned_interactions", {})
    to_remove_ab = [k for k, v in abandoned.items() if v.get("timestamp", "") < seven_days_ago]
    for k in to_remove_ab:
        abandoned.pop(k)
        modified = True

    rec_failures = store.setdefault("recommendation_failures", {})
    to_remove_rec_fail = [k for k, v in rec_failures.items() if v.get("timestamp", "") < seven_days_ago]
    for k in to_remove_rec_fail:
        rec_failures.pop(k)
        modified = True

    if modified:
        save_personality_store()
        clear_all_personality_caches()
