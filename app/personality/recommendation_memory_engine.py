from app.personality.recommendation_reinforcement_engine import reinforce_recommendation
from app.personality.personality_models import RecommendationMemoryNode

def record_recommendation_use(
    item: str,
    category: str,
    accepted: bool
) -> RecommendationMemoryNode:
    """
    Direct proxy method to update recommendation reinforcement scores.
    """
    return reinforce_recommendation(item, category, accepted)
