from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class EntityNode(BaseModel):
    entity_id: str
    name: str
    canonical_name: str
    entity_type: str
    aliases: List[str] = []
    mentions: int = 1
    confidence: float = 1.0
    sources: List[str] = []
    supporting_modalities: List[str] = []
    created_at: str
    updated_at: str
    last_seen: str
    importance_score: float = 0.0
    centrality_score: float = 0.0
    community_id: Optional[str] = None

class RelationNode(BaseModel):
    relation_id: str
    source_entity: str
    target_entity: str
    relation_type: str
    confidence: float
    weight: float
    created_at: str
    updated_at: str
    evidence_ids: List[str] = []
    source_modalities: List[str] = []
    created_by: str
    last_confirmed: str
    confirmation_count: int = 1

class TemporalNode(BaseModel):
    event_id: str
    description: str
    timestamp: str
    entities: List[str] = []
    event_type: str
    created_at: str
    updated_at: str
    last_seen: str

class CommunityNode(BaseModel):
    community_id: str
    entities: List[str]
    importance: float = 0.0
    community_center_entity: Optional[str] = None

class SubgraphNode(BaseModel):
    subgraph_id: str
    entities: List[str]
    relations: List[str]

class GraphResponse(BaseModel):
    answer: str
    confidence: str
    entities: List[Dict[str, Any]] = []
    relations: List[Dict[str, Any]] = []
    subgraph: Dict[str, Any] = {}
    why_this_answer: List[str] = []
