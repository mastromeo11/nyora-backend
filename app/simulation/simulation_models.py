from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class WorldStateNode(BaseModel):
    world_state_id: str
    entities: List[str] = []
    relations: List[Dict[str, Any]] = []
    timestamp: str
    importance_score: float = 0.0
    confidence: float = 1.0
    summary: str
    embedding: Optional[List[float]] = None
    entity_distribution: Dict[str, int] = {}
    tool_distribution: Dict[str, int] = {}
    agent_distribution: Dict[str, int] = {}
    failure_distribution: Dict[str, int] = {}
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    parent_world_state: Optional[str] = None

class HypothesisNode(BaseModel):
    hypothesis_id: str
    description: str
    supporting_entities: List[str] = []
    supporting_evidence: List[str] = []
    confidence: float = 1.0
    created_at: str
    last_confirmed: str
    confirmation_count: int = 1
    supporting_episode_ids: List[str] = []
    supporting_pattern_ids: List[str] = []
    supporting_evidence_ids: List[str] = []
    embedding: Optional[List[float]] = None

class ScenarioNode(BaseModel):
    scenario_id: str
    parent_state: str
    child_states: List[str] = []
    summary: str
    success_probability: float = 1.0
    risk_score: float = 0.0
    importance_score: float = 0.0
    embedding: Optional[List[float]] = None
    reinforcement_score: float = 0.0

class CounterfactualNode(BaseModel):
    counterfactual_id: str
    base_scenario: str
    modified_variable: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    alternative_outcome: str
    risk_delta: float = 0.0
    confidence: float = 1.0
    embedding: Optional[List[float]] = None

class SimulationNode(BaseModel):
    simulation_id: str
    initial_state: str
    final_state: str
    scenario_chain: List[str] = []
    score: float = 0.0
    timestamp: str
    planner_trace_ids: List[str] = []
    critic_trace_ids: List[str] = []
    consensus_trace_ids: List[str] = []
    agent_ids: List[str] = []
    tool_ids: List[str] = []
    embedding: Optional[List[float]] = None
    reinforcement_score: float = 0.0

class PolicyNode(BaseModel):
    policy_id: str
    actions: List[str] = []
    success_rate: float = 1.0
    confidence: float = 1.0
    frequency: int = 1
    success_count: int = 1
    last_used: str
    last_success: Optional[str] = None
    average_latency: float = 0.0
    average_confidence: float = 1.0
    reinforcement_score: float = 0.0

class PolicyFailureNode(BaseModel):
    policy_id: str
    failure_count: int = 0
    timeout_count: int = 0
    oom_count: int = 0
    tool_failures: List[str] = []
    last_failure: str

class FailureForecastNode(BaseModel):
    failure_forecast_id: str
    failure_type: str
    risk_score: float = 0.0
    probability: float = 0.0
    entities: List[str] = []
    embedding: Optional[List[float]] = None

# Failure Forecast subclasses
class ToolTimeoutForecast(FailureForecastNode):
    timeout_threshold_seconds: float = 30.0

class OOMForecast(FailureForecastNode):
    memory_limit_gb: float = 16.0

class AgentCrashForecast(FailureForecastNode):
    crash_reason: str = "Unknown"

class DatabaseFailureForecast(FailureForecastNode):
    database_name: str = "ChromaDB"

class NetworkFailureForecast(FailureForecastNode):
    network_endpoint: str = "Ollama"

class FailureSimulationNode(BaseModel):
    failure_simulation_id: str
    simulation_id: str
    failure_type: str
    tool_failures: List[str] = []
    agent_failures: List[str] = []
    timeout_events: int = 0
    risk_score: float = 0.0
    frequency: int = 1
    last_seen: str

class ScenarioSummaryNode(BaseModel):
    summary_id: str
    scenario_id: str
    summary: str
    major_events: List[str] = []
    milestones: List[str] = []
    successes: int = 0
    failures: int = 0
    entities: List[str] = []

class SimulationArchiveNode(BaseModel):
    archive_id: str
    simulation_ids: List[str] = []
    summary_text: str
    milestones: List[str] = []
    timestamp: str

# Future Placeholders
class ToolLearningNode(BaseModel):
    tool_learning_id: str
    tool_name: str
    usage_pattern: str
    timestamp: str

class PlannerPolicyNode(BaseModel):
    policy_id: str
    goal_type: str
    decision_sequence: List[str] = []
    timestamp: str

class HumanPreferenceNode(BaseModel):
    preference_id: str
    user_id: str
    preference_key: str
    preference_value: str
    timestamp: str

class EmotionNode(BaseModel):
    emotion_id: str
    state_description: str
    valence: float
    arousal: float
    timestamp: str
