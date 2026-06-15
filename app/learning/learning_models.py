from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class PatternNode(BaseModel):
    pattern_id: str
    signature: str
    frequency: int = 1
    success_count: int = 1
    confidence: float = 1.0
    importance_score: float = 0.0
    supporting_entities: List[str] = []
    evidence_ids: List[str] = []
    source_modalities: List[str] = []
    last_confirmed: str
    confirmation_count: int = 1
    created_at: str

class CorrectionNode(BaseModel):
    correction_id: str
    reason: str
    reflection_ids: List[str] = []
    replanning_ids: List[str] = []
    evidence_ids: List[str] = []
    source_modalities: List[str] = []
    confirmation_count: int = 1
    last_confirmed: str
    original_answer: Optional[str] = None
    corrected_answer: Optional[str] = None
    confidence: float = 1.0
    timestamp: str
    source: str = "correction_engine"

class FeedbackNode(BaseModel):
    feedback_id: str
    query: str
    answer: str
    feedback_type: str  # SUCCESS, FAILURE, CORRECTION, LOW_CONFIDENCE, RETRY
    confidence: float
    timestamp: str

class LearningNode(BaseModel):
    learning_id: str
    learning_type: str
    content: str
    importance: float = 0.0
    confidence: float = 1.0
    timestamp: str

class QueryClusterNode(BaseModel):
    cluster_id: str
    cluster_center_query: str
    queries: List[str] = []
    entities: List[str] = []
    frequency: int = 1
    importance_score: float = 0.0
    success_rate: float = 1.0
    entity_distribution: Dict[str, float] = {}

class FailurePatternNode(BaseModel):
    failure_pattern_id: str
    failure_type: str  # timeout, tool_crash, grounding_failure, restart_loop, etc.
    tool_failures: List[str] = []
    grounding_failures: List[str] = []
    timeout_count: int = 0
    restart_count: int = 0
    confidence: float = 1.0
    last_seen: str
    created_at: str

class LearningResponse(BaseModel):
    answer: str
    confidence: str
    patterns: List[Dict[str, Any]] = []
    corrections: List[Dict[str, Any]] = []
    feedback_used: List[Dict[str, Any]] = []
    why_this_answer: List[str] = []

# Reserved Types for future Milestone 13 Swarm implementations:
# AgentNode, DelegationNode, CollaborationNode, SharedMemoryNode, NegotiationNode, ConsensusNode, MessageNode
class AgentNode(BaseModel):
    agent_id: str
    agent_name: str
    role: str
    capabilities: List[str] = []
    confidence: float = 1.0

class DelegationNode(BaseModel):
    delegation_id: str
    sender_agent: str
    receiver_agent: str
    task_description: str
    timestamp: str

class CollaborationNode(BaseModel):
    collaboration_id: str
    participants: List[str]
    context: str
    timestamp: str
