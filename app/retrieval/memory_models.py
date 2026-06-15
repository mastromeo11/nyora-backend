from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class MemoryNode(BaseModel):
    """
    Unified MemoryNode abstraction. Standardized for conversational history,
    summaries, entity records, and future agent observations or reflections.
    """
    memory_id: str
    memory_type: str  # e.g., 'turn_node', 'summary_node', 'preference_node', 'entity_node'
    content: str
    source: str
    score: float
    timestamp: str
    importance: float

class ConversationTurn(BaseModel):
    turn_id: str
    session_id: str
    user_query: str
    assistant_answer: str
    timestamp: str
    retrieved_sources: List[str]
    entities: List[str]
    intent_profile: str
    confidence: str

class EntityMemory(BaseModel):
    entity_name: str
    mentions: int
    last_seen: str
    sources: List[str]
    supporting_modalities: List[str]
    confidence: float

class PreferenceMemory(BaseModel):
    key: str
    value: str
    timestamp: str

class ConversationSummary(BaseModel):
    session_id: str
    summary: str
    entity_focus: List[str]
    important_facts: List[str]
    timestamp: str

class MemoryResponse(BaseModel):
    memory_used: bool
    session_summary: str
    active_entities: List[str]
    memory_sources: List[str]
