import uuid
from datetime import datetime
from typing import List, Optional
from app.personality.personality_store import get_preferences, append_preference
from app.personality.personality_models import HumanPreferenceNode
from app.personality.preference_signature_engine import generate_preference_signature
from app.personality.privacy_filter_engine import filter_sensitive_info

def record_preference_run(
    domain: str,
    tone: str,
    response_length: int,
    explanation_depth: str,
    success: bool,
    confidence: float = 0.5,
    user_entities: List[str] = []
) -> HumanPreferenceNode:
    """
    Records a user preference run. Normalizes domain/tone, runs privacy filter,
    calculates signature to prevent duplicates, and updates preference scores.
    """
    # 1. Enforce sensitive data filter
    clean_domain, d_filtered = filter_sensitive_info(domain)
    clean_tone, t_filtered = filter_sensitive_info(tone)
    clean_entities = []
    for ent in (user_entities or []):
        c_ent, ent_filtered = filter_sensitive_info(ent)
        clean_entities.append(c_ent)

    sig = generate_preference_signature(clean_domain, clean_tone, response_length, explanation_depth)
    
    prefs = get_preferences()
    node = None
    for p in prefs:
        if getattr(p, "signature", None) == sig:
            node = p
            break

    if node is None:
        node = HumanPreferenceNode(
            preference_id=f"pref_{uuid.uuid4().hex[:8]}",
            user_entities=clean_entities,
            preferred_domains=[clean_domain],
            explanation_depth=explanation_depth,
            tone_preference=clean_tone,
            response_length=response_length,
            confidence=confidence,
            frequency=0,
            timestamp=datetime.utcnow().isoformat(),
            signature=sig
        )

    node.frequency += 1
    node.timestamp = datetime.utcnow().isoformat()
    if clean_domain not in node.preferred_domains:
        node.preferred_domains.append(clean_domain)
    node.user_entities = list(set(node.user_entities + clean_entities))

    # Calculate success and confidence reinforcement updates
    # EMA success rate update
    hist_success = node.success_rate
    recent_success = 1.0 if success else 0.0
    new_success = 0.7 * hist_success + 0.3 * recent_success
    node.success_rate = new_success

    # Calibrate confidence using personality_confidence_calibrator if available
    try:
        from app.personality.personality_confidence_calibrator import calibrate_personality_confidence
        node.confidence = calibrate_personality_confidence(
            historical_conf=node.confidence,
            historical_success=hist_success,
            recent_success=recent_success,
            recent_outcome=recent_success,
            recency=1.0
        )
    except Exception:
        # Fallback reinforcement
        if success:
            node.confidence = 0.7 * node.confidence + 0.3 * confidence
        else:
            node.confidence *= 0.8

    append_preference(node)
    
    # Trigger archive checks
    try:
        from app.personality.personality_archive_engine import archive_old_personalities_if_needed
        archive_old_personalities_if_needed()
    except Exception as e:
        print(f"[PREFERENCE ENGINE] Error triggering archives: {e}")

    return node

def get_preference_score(node: HumanPreferenceNode) -> float:
    """
    Computes dynamic preference score:
    score = 0.4 * frequency + 0.3 * success + 0.2 * recency + 0.1 * confidence
    """
    freq_score = min(node.frequency / 10.0, 1.0)
    success_score = node.success_rate
    recency = 1.0  # Default recency
    score = (
        0.4 * freq_score +
        0.3 * success_score +
        0.2 * recency +
        0.1 * node.confidence
    )

    return min(max(score, 0.0), 1.0)
