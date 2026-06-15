from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class GoalNode(BaseModel):
    goal_id: str
    query: str
    goal_type: str
    timestamp: str

class PlanNode(BaseModel):
    plan_id: str
    goal_id: str
    steps: List[str]
    status: str

class TaskNode(BaseModel):
    task_id: str
    description: str
    dependency_ids: List[str]
    status: str

class ToolNode(BaseModel):
    tool_name: str
    execution_time: float
    success: bool

class ObservationNode(BaseModel):
    observation_id: str
    tool_name: str
    content: str
    timestamp: str

class ReflectionNode(BaseModel):
    reflection_id: str
    reason: str
    failure_type: str
    timestamp: str

class TraceNode(BaseModel):
    trace_id: str
    goal_id: str
    plan_id: str
    steps: List[str]
    success: bool

class AgentResponse(BaseModel):
    answer: str
    confidence: str
    sources: List[Dict[str, Any]]
    goal: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None
    observations: List[Dict[str, Any]] = []
    reflections: List[Dict[str, Any]] = []
    why_this_answer: List[str] = []
