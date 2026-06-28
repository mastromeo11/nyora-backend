from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ToolLearningNode(BaseModel):
    tool_id: str
    tool_name: str
    frequency: int = 0
    success_rate: float = 1.0
    timeout_count: int = 0
    failure_count: int = 0
    latency_ms: float = 0.0
    latency_score: float = 1.0
    confidence: float = 1.0
    importance_score: float = 1.0
    last_used: str
    embedding: Optional[List[float]] = None
    timeout_rate: float = 0.0
    latency_variance: float = 0.0
    failure_rate: float = 0.0
    latency_history: List[float] = []

class PlannerPolicyNode(BaseModel):
    policy_id: str
    planner_type: str
    success_rate: float = 1.0
    confidence: float = 1.0
    importance: float = 1.0
    frequency: int = 0
    latency_score: float = 1.0
    recency: float = 1.0
    signature: str
    tool_sequence: List[str] = []
    success_count: int = 0
    failure_count: int = 0
    average_latency: float = 0.0
    confidence_variance: float = 0.0
    confidence_history: List[float] = []

class MetaReflectionNode(BaseModel):
    reflection_id: str
    query_signature: str
    reflection_summary: str
    issues_detected: List[str] = []
    recommendations: List[str] = []
    timestamp: str

class StrategyNode(BaseModel):
    strategy_id: str
    query_pattern: str
    planner_id: str
    tool_ids: List[str] = []
    success_rate: float = 1.0
    confidence: float = 1.0
    frequency: int = 0
    signature: Optional[str] = None

class PolicyReplayNode(BaseModel):
    replay_id: str
    source_policy: str
    target_policy: str
    similarity: float = 1.0
    frequency: int = 1
    success_count: int = 1

class ToolFailureNode(BaseModel):
    failure_id: str
    tool_name: str
    failure_type: str
    frequency: int = 0
    last_seen: str

class PolicyFailureNode(BaseModel):
    failure_id: str
    policy_id: str
    failure_reason: str
    frequency: int = 0
    last_seen: str

class ReflectionFailureNode(BaseModel):
    failure_id: str
    reflection_id: str
    failure_type: str
    frequency: int = 0
    last_seen: str

class OptimizationFailureNode(BaseModel):
    failure_id: str
    query: str
    failure_reason: str
    frequency: int = 0
    last_seen: str

class PolicySummaryNode(BaseModel):
    summary_id: str
    policy_ids: List[str] = []
    summary: str
    successes: int = 0
    failures: int = 0

class PolicyArchiveNode(BaseModel):
    archive_id: str
    summary_id: str
    timestamp: str
    summaries: List[str] = []
    tool_distributions: Dict[str, int] = {}
    success_metrics: Dict[str, float] = {}
    confidence_distributions: Dict[str, float] = {}
    latency_distributions: Dict[str, float] = {}

class MetaArchiveNode(BaseModel):
    archive_id: str
    timestamp: str
    archived_strategies: List[Dict[str, Any]] = []
    archived_reflections: List[Dict[str, Any]] = []
    archived_policy_summaries: List[Dict[str, Any]] = []

class PolicySimilarityNode(BaseModel):
    source_policy: str
    target_policy: str
    similarity: float
    timestamp: str
    frequency: int = 1

class MetaResponse(BaseModel):
    explanation: str
    tool_ranking: List[Dict[str, Any]] = []
    policy_ranking: List[Dict[str, Any]] = []

# Milestone 17 Placeholders
class HumanPreferenceNode(BaseModel):
    preference_id: str
    user_id: str
    preference_key: str
    preference_value: str
    timestamp: str

class UserStyleNode(BaseModel):
    style_id: str
    user_id: str
    style_key: str
    style_value: str
    timestamp: str

class AdaptivePersonalityNode(BaseModel):
    personality_id: str
    trait_key: str
    trait_value: float
    timestamp: str

class EmotionNode(BaseModel):
    emotion_id: str
    state_description: str
    valence: float
    arousal: float
    timestamp: str
