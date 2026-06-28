from datetime import datetime
from typing import List, Dict, Any, Set, Tuple

from app.config import (
    ENABLE_HUMAN_PREFERENCES,
    MAX_PERSONALITY_DEPTH,
    MAX_TOTAL_PERSONALITIES_VISITED,
    STYLE_WEIGHT,
    SUCCESS_WEIGHT,
    CONFIDENCE_WEIGHT,
    RECENCY_WEIGHT,
    IMPORTANCE_WEIGHT,
    FREQUENCY_WEIGHT
)
from app.personality.personality_store import (
    get_preferences,
    get_user_styles,
    get_adaptive_personalities,
    get_interaction_memories
)
from app.personality.personality_models import HumanPreferenceNode

def calculate_recency(timestamp_str: str) -> float:
    """
    Calculates a recency score between 0.0 and 1.0 based on age.
    """
    try:
        dt = datetime.fromisoformat(timestamp_str)
        delta = datetime.utcnow() - dt
        days = max(0.0, delta.total_seconds() / 86400.0)
        return 1.0 / (1.0 + days)
    except Exception:
        return 0.5

def get_relevant_preferences(query: str) -> List[Tuple[HumanPreferenceNode, float]]:
    """
    Retrieves and ranks preferences for the query using a hybrid scoring algorithm.
    Ensures loop checks using visited sets when traversing relationships.
    """
    if not ENABLE_HUMAN_PREFERENCES:
        return []

    query_lower = query.lower()
    prefs = get_preferences()
    scored_prefs = []

    visited_nodes: Set[str] = set()

    # Get style nodes and interaction memories to compute style and success scores
    styles = {s.style_id: s for s in get_user_styles()}
    interactions = get_interaction_memories()

    for pref in prefs:
        if len(visited_nodes) >= MAX_TOTAL_PERSONALITIES_VISITED:
            break

        if pref.preference_id in visited_nodes:
            continue
        visited_nodes.add(pref.preference_id)

        # 1. Domain Match
        domain_match = 0.0
        if pref.preferred_domains:
            matches = sum(1 for d in pref.preferred_domains if d.lower() in query_lower)
            domain_match = matches / len(pref.preferred_domains)

        # 2. Entity Match
        entity_match = 0.0
        if pref.user_entities:
            matches = sum(1 for e in pref.user_entities if e.lower() in query_lower)
            entity_match = matches / len(pref.user_entities)

        # Combine domain and entity matches for relevance context
        relevance = max(domain_match, entity_match) if (pref.preferred_domains or pref.user_entities) else 0.5

        # 3. Confidence Score
        confidence = pref.confidence

        # 4. Recency Score
        recency = calculate_recency(pref.timestamp)

        # 5. Frequency Score
        freq_val = min(1.0, pref.frequency / 10.0)

        # 6. Success Score
        # Match with interaction memories to find the success score of this topic/domain
        success_rates = []
        for interact in interactions:
            if interact.topic.lower() in query_lower:
                success_rates.append(interact.success_score)
        success = sum(success_rates) / len(success_rates) if success_rates else 1.0

        # 7. Style Score
        # Check if there is a matching style node
        style_val = 0.5
        for s_id, s in styles.items():
            if s.writing_style.lower() in pref.tone_preference.lower():
                style_val = s.confidence
                break

        # 8. Importance (default to confidence if not separate)
        importance = confidence

        # Hybrid formula
        score = (
            (style_val * STYLE_WEIGHT) +
            (success * SUCCESS_WEIGHT) +
            (confidence * CONFIDENCE_WEIGHT) +
            (recency * RECENCY_WEIGHT) +
            (importance * IMPORTANCE_WEIGHT) +
            (freq_val * FREQUENCY_WEIGHT)
        )

        # Multiply by relevance to prioritize topic-specific preferences
        final_score = score * (0.3 + 0.7 * relevance)
        scored_prefs.append((pref, final_score))

    # Sort descending
    scored_prefs.sort(key=lambda x: x[1], reverse=True)
    return scored_prefs
