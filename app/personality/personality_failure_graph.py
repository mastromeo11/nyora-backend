from typing import List, Dict, Any
from app.personality.personality_models import (
    PersonalityFailureNode,
    NegativePreferenceNode,
    AbandonedInteractionNode
)

def build_personality_failure_graph(
    failures: List[PersonalityFailureNode],
    negatives: List[NegativePreferenceNode],
    abandoned: List[AbandonedInteractionNode]
) -> Dict[str, Any]:
    """
    Constructs an isolated failure graph from user dissatisfaction data.
    This graph does not connect to successful style profiles.
    """
    nodes = []
    edges = []

    # Assemble nodes
    for fn in failures:
        nodes.append({
            "id": fn.failure_id,
            "type": "personality_failure",
            "reason": fn.dissatisfaction_reason,
            "abandoned": fn.abandoned_interaction,
            "feedback": fn.negative_feedback
        })

    for nn in negatives:
        nodes.append({
            "id": nn.preference_id,
            "type": "negative_preference",
            "disliked_style": nn.disliked_style,
            "disliked_format": nn.disliked_format
        })

    for an in abandoned:
        nodes.append({
            "id": an.interaction_id,
            "type": "abandoned_interaction",
            "query": an.query,
            "failure_reason": an.failure_reason
        })

    # Add edges within failure structures
    for fn in failures:
        for nn in negatives:
            if nn.disliked_style in fn.dissatisfaction_reason or nn.disliked_format in fn.dissatisfaction_reason:
                edges.append({
                    "source": nn.preference_id,
                    "target": fn.failure_id,
                    "type": "negative_preference_to_failure"
                })

    for an in abandoned:
        for fn in failures:
            if an.failure_reason in fn.dissatisfaction_reason or fn.dissatisfaction_reason in an.failure_reason:
                edges.append({
                    "source": an.interaction_id,
                    "target": fn.failure_id,
                    "type": "abandoned_to_failure"
                })

    return {"nodes": nodes, "edges": edges}
