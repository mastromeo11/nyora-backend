import uuid
from datetime import datetime
from app.personality.personality_models import (
    PersonalityFailureNode,
    NegativePreferenceNode,
    AbandonedInteractionNode,
    RecommendationFailureNode
)
from app.personality.personality_store import (
    append_personality_failure,
    append_negative_preference,
    append_abandoned_interaction,
    append_recommendation_failure
)

def record_dissatisfaction(reason: str, feedback: str) -> PersonalityFailureNode:
    """
    Logs dissatisfaction feedback in an isolated failure node.
    """
    node = PersonalityFailureNode(
        failure_id=f"fail_{uuid.uuid4().hex[:8]}",
        dissatisfaction_reason=reason,
        abandoned_interaction=False,
        negative_feedback=feedback,
        timestamp=datetime.utcnow().isoformat()
    )
    append_personality_failure(node)
    return node

def record_negative_preference(user_id: str, disliked_style: str, disliked_format: str) -> NegativePreferenceNode:
    """
    Saves a negative preference indicating elements the user explicitly dislikes.
    """
    node = NegativePreferenceNode(
        preference_id=f"neg_pref_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        disliked_style=disliked_style,
        disliked_format=disliked_format,
        confidence=1.0,
        frequency=1,
        timestamp=datetime.utcnow().isoformat()
    )
    append_negative_preference(node)
    return node

def record_abandoned_interaction(query: str, reason: str) -> AbandonedInteractionNode:
    """
    Saves an interaction abandonment trace.
    """
    node = AbandonedInteractionNode(
        interaction_id=f"aband_{uuid.uuid4().hex[:8]}",
        query=query,
        timestamp=datetime.utcnow().isoformat(),
        failure_reason=reason
    )
    append_abandoned_interaction(node)
    return node

def record_recommendation_failure(rejected_item: str, disliked_style: str) -> RecommendationFailureNode:
    """
    Logs rejected tools or recommended content.
    """
    node = RecommendationFailureNode(
        failure_id=f"rec_fail_{uuid.uuid4().hex[:8]}",
        rejected_item=rejected_item,
        disliked_style=disliked_style,
        abandoned_recommendation=True,
        timestamp=datetime.utcnow().isoformat()
    )
    append_recommendation_failure(node)
    return node
