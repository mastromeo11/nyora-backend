from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class HumanPreferenceNode(BaseModel):
    preference_id: str
    user_entities: List[str] = []
    preferred_domains: List[str] = []
    explanation_depth: str = "medium"
    tone_preference: str = "professional"
    response_length: int = 200
    confidence: float = 0.5
    frequency: int = 1
    success_rate: float = 1.0
    timestamp: str
    signature: Optional[str] = None


class NegativePreferenceNode(BaseModel):
    preference_id: str
    user_id: str
    disliked_style: str
    disliked_format: str
    confidence: float = 0.5
    frequency: int = 1
    timestamp: str

class UserStyleNode(BaseModel):
    style_id: str
    writing_style: str
    verbosity: str
    formatting_style: str
    emoji_usage: bool = False
    examples: List[str] = []
    confidence: float = 0.5

class AdaptivePersonalityNode(BaseModel):
    personality_id: str
    personality_type: str
    speaking_patterns: List[str] = []
    explanation_preferences: List[str] = []
    confidence: float = 0.5
    reinforcement_count: int = 0

class InteractionMemoryNode(BaseModel):
    interaction_id: str
    topic: str
    task_type: str
    success_score: float = 1.0
    frequency: int = 1
    confidence: float = 0.5

class RecommendationMemoryNode(BaseModel):
    recommendation_id: str
    item: str
    category: str
    accepted: bool
    rejected: bool
    confidence: float = 0.5
    frequency: int = 1
    signature: Optional[str] = None

class PersonalityReplayNode(BaseModel):
    replay_id: str
    source_personality: str
    target_query: str
    similarity_score: float = 0.0

class PersonalityFailureNode(BaseModel):
    failure_id: str
    dissatisfaction_reason: str
    abandoned_interaction: bool
    negative_feedback: str
    timestamp: str

class AbandonedInteractionNode(BaseModel):
    interaction_id: str
    query: str
    timestamp: str
    failure_reason: str

class RecommendationFailureNode(BaseModel):
    failure_id: str
    rejected_item: str
    disliked_style: str
    abandoned_recommendation: bool
    timestamp: str

class InteractionSummaryNode(BaseModel):
    summary_id: str
    summary_text: str
    major_topics: List[str] = []
    successful_domains: List[str] = []
    response_patterns: List[str] = []
    accepted_recommendations: List[str] = []

class PersonalitySummaryNode(BaseModel):
    summary_id: str
    summary_text: str
    major_preferences: List[str] = []
    styles: List[str] = []
    habits: List[str] = []

class PersonalityArchiveNode(BaseModel):
    archive_id: str
    timestamp: str
    archived_preferences: List[Dict[str, Any]] = []
    archived_styles: List[Dict[str, Any]] = []
    archived_personalities: List[Dict[str, Any]] = []

class PersonalitySimilarityNode(BaseModel):
    source_personality: str
    target_personality: str
    similarity: float
    frequency: int = 1
    last_seen: str

class PersonalizationResponse(BaseModel):
    explanation: str
    preference_applied: bool
    personality_type: str

# Milestone 18 placeholders
class EmotionNode(BaseModel):
    emotion_id: str
    emotion_type: str
    intensity: float
    timestamp: str

class MoodNode(BaseModel):
    mood_id: str
    mood_type: str
    valence: float
    timestamp: str

class VisualThemeNode(BaseModel):
    theme_id: str
    theme_name: str
    colors: Dict[str, str] = {}

class UILayoutNode(BaseModel):
    layout_id: str
    components: List[str] = []

class AdaptiveInterfaceNode(BaseModel):
    interface_id: str
    adaptive_mode: str
    settings: Dict[str, Any] = {}
