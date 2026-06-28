from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class EpisodeNode(BaseModel):
    episode_id: str
    timestamp: str
    query: str
    answer: str
    entities: List[str] = []
    agent_trace_ids: List[str] = []
    importance_score: float = 0.0
    confidence: float = 1.0  # Decays numerically
    experience_type: str = "general"
    supporting_evidence_ids: List[str] = []
    summary: str
    created_at: str
    updated_at: str
    last_accessed: str
    query_embedding: Optional[List[float]] = None
    summary_embedding: Optional[List[float]] = None
    cluster_id: Optional[str] = None
    access_count: int = 0
    planner_trace_ids: List[str] = []
    critic_trace_ids: List[str] = []
    consensus_trace_ids: List[str] = []
    agent_ids: List[str] = []

class ExperienceNode(BaseModel):
    experience_id: str
    episode_id: str
    tools_used: List[str] = []
    agent_trace_ids: List[str] = []
    reflection_ids: List[str] = []
    consensus_ids: List[str] = []
    success_status: bool = True
    execution_latency: float = 0.0
    failure_reason: Optional[str] = None
    importance_score: float = 0.0
    confidence: float = 1.0
    timestamp: str

class ReplayNode(BaseModel):
    replay_id: str
    source_episode: str
    target_episode: str
    similarity_score: float = 0.0
    timestamp: str
    frequency: int = 1
    success_count: int = 1
    last_seen: str
    score: float = 0.0

class TemporalChainNode(BaseModel):
    chain_id: str
    episode_ids: List[str] = []
    chain_summary: Optional[str] = None
    chain_importance: float = 0.0
    created_at: str
    updated_at: str

class MemoryClusterNode(BaseModel):
    cluster_id: str
    episodes: List[str] = []
    cluster_center_query: str
    cluster_center_embedding: Optional[List[float]] = None
    frequency: int = 1
    importance_score: float = 0.0
    success_rate: float = 1.0
    last_updated: str

class FailureReplayNode(BaseModel):
    failure_replay_id: str
    failure_type: str
    tool_failures: List[str] = []
    agent_failures: List[str] = []
    timeout_events: int = 0
    frequency: int = 1
    last_seen: str

class ChainSummaryNode(BaseModel):
    chain_summary_id: str
    chain_id: str
    summary_text: str
    major_entities: List[str] = []
    successes: int = 0
    failures: int = 0
    milestones: List[str] = []
    timestamp: str

class EpisodicResponse(BaseModel):
    answer: str
    confidence: str
    episodes: List[Dict[str, Any]] = []
    replays: List[Dict[str, Any]] = []
    summary: str
    why_this_answer: str

# Future Milestone Placeholders
class SimulationNode(BaseModel):
    simulation_id: str
    scenario_id: str
    variables: Dict[str, Any] = {}
    outcomes: List[str] = []
    timestamp: str

class HypothesisNode(BaseModel):
    hypothesis_id: str
    statement: str
    evidence_ids: List[str] = []
    status: str = "pending"
    timestamp: str

class ScenarioNode(BaseModel):
    scenario_id: str
    description: str
    parameters: Dict[str, Any] = {}
    timestamp: str

class WorldStateNode(BaseModel):
    state_id: str
    state_vector: List[float] = []
    description: str
    timestamp: str

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
