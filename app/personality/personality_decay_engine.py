from app.config import (
    ENABLE_PERSONALITY_DECAY,
    PERSONALITY_DECAY_FACTOR,
    STYLE_DECAY_FACTOR,
    PREFERENCE_DECAY_FACTOR
)
from app.personality.personality_store import load_personality_store, save_personality_store

def decay_personality_memory():
    """
    Decays the confidence, frequency, and related weights of all active nodes
    in the personality database based on decay factors.
    """
    if not ENABLE_PERSONALITY_DECAY:
        return

    store = load_personality_store()

    # 1. Decay Human Preferences
    preferences = store.setdefault("preferences", {})
    for pref_id, pref in preferences.items():
        if "confidence" in pref:
            pref["confidence"] = max(0.01, pref["confidence"] * PREFERENCE_DECAY_FACTOR)
        if "frequency" in pref:
            # Keep frequency as float or int, if model demands int, store it as int
            pref["frequency"] = max(1, int(pref["frequency"] * PREFERENCE_DECAY_FACTOR))

    # 2. Decay User Styles
    user_styles = store.setdefault("user_styles", {})
    for style_id, style in user_styles.items():
        if "confidence" in style:
            style["confidence"] = max(0.01, style["confidence"] * STYLE_DECAY_FACTOR)

    # 3. Decay Adaptive Personalities
    adaptive_personalities = store.setdefault("adaptive_personalities", {})
    for pers_id, pers in adaptive_personalities.items():
        if "confidence" in pers:
            pers["confidence"] = max(0.01, pers["confidence"] * PERSONALITY_DECAY_FACTOR)

    # 4. Decay Interaction Memories
    interaction_memories = store.setdefault("interaction_memories", {})
    for int_id, interaction in interaction_memories.items():
        if "confidence" in interaction:
            interaction["confidence"] = max(0.01, interaction["confidence"] * PERSONALITY_DECAY_FACTOR)
        if "frequency" in interaction:
            interaction["frequency"] = max(1, int(interaction["frequency"] * PERSONALITY_DECAY_FACTOR))

    # 5. Decay Recommendation Memories
    recommendation_memories = store.setdefault("recommendation_memories", {})
    for rec_id, rec in recommendation_memories.items():
        if "confidence" in rec:
            rec["confidence"] = max(0.01, rec["confidence"] * PERSONALITY_DECAY_FACTOR)
        if "frequency" in rec:
            rec["frequency"] = max(1, int(rec["frequency"] * PERSONALITY_DECAY_FACTOR))

    # Save decayed data back to disk
    save_personality_store()
