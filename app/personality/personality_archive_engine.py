import uuid
from datetime import datetime
from typing import Optional

from app.config import (
    MAX_PERSONALITIES,
    MAX_USER_STYLES,
    ENABLE_PERSONALITY_ARCHIVES
)
from app.personality.personality_models import PersonalityArchiveNode
from app.personality.personality_store import (
    load_personality_store,
    save_personality_store,
    append_personality_archive
)

def archive_old_personality_data(force: bool = False) -> Optional[PersonalityArchiveNode]:
    """
    Compresses and archives old preferences, styles, and adaptive personality nodes
    into a PersonalityArchiveNode when their count exceeds defined thresholds.
    """
    if not ENABLE_PERSONALITY_ARCHIVES and not force:
        return None

    store = load_personality_store()
    
    preferences = store.setdefault("preferences", {})
    user_styles = store.setdefault("user_styles", {})
    adaptive_personalities = store.setdefault("adaptive_personalities", {})

    archived_prefs = []
    archived_styles = []
    archived_pers = []

    # Archive preferences if count > 100 (or MAX_PERSONALITIES)
    # Let's use MAX_PERSONALITIES as the preference capacity threshold
    if len(preferences) > MAX_PERSONALITIES or force:
        # Sort by timestamp ascending (oldest first)
        sorted_keys = sorted(
            preferences.keys(),
            key=lambda k: preferences[k].get("timestamp", "")
        )
        # Archive all except the latest 5
        num_to_archive = max(0, len(preferences) - 5) if force else max(0, len(preferences) - MAX_PERSONALITIES)
        if num_to_archive > 0:
            for k in sorted_keys[:num_to_archive]:
                archived_prefs.append(preferences.pop(k))

    # Archive styles if count > MAX_USER_STYLES
    if len(user_styles) > MAX_USER_STYLES or force:
        # UserStyleNode does not have timestamp, but has confidence. Let's sort by confidence ascending (lowest first)
        sorted_keys = sorted(
            user_styles.keys(),
            key=lambda k: user_styles[k].get("confidence", 0.0)
        )
        num_to_archive = max(0, len(user_styles) - 5) if force else max(0, len(user_styles) - MAX_USER_STYLES)
        if num_to_archive > 0:
            for k in sorted_keys[:num_to_archive]:
                archived_styles.append(user_styles.pop(k))

    # Archive personalities if count > MAX_PERSONALITIES
    if len(adaptive_personalities) > MAX_PERSONALITIES or force:
        # Sort by confidence ascending
        sorted_keys = sorted(
            adaptive_personalities.keys(),
            key=lambda k: adaptive_personalities[k].get("confidence", 0.0)
        )
        num_to_archive = max(0, len(adaptive_personalities) - 5) if force else max(0, len(adaptive_personalities) - MAX_PERSONALITIES)
        if num_to_archive > 0:
            for k in sorted_keys[:num_to_archive]:
                archived_pers.append(adaptive_personalities.pop(k))

    if not archived_prefs and not archived_styles and not archived_pers:
        return None

    # Create archive node
    archive_node = PersonalityArchiveNode(
        archive_id=f"archive_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.utcnow().isoformat(),
        archived_preferences=archived_prefs,
        archived_styles=archived_styles,
        archived_personalities=archived_pers
    )

    # Save to store and update storage
    append_personality_archive(archive_node)
    save_personality_store()

    return archive_node

def archive_old_personalities_if_needed():
    """
    Wrapper function matching the import in human_preference_engine.py.
    """
    return archive_old_personality_data(force=False)

