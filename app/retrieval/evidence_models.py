from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class EvidenceNode(BaseModel):
    evidence_id: str
    source: str
    source_type: str
    modality: str  # text, ocr, image, caption, vqa, audio
    content: str
    retrieval_score: float
    confidence: str  # High, Medium, Low
    citation_reason: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None
    visual_category: Optional[str] = None
    file_path: Optional[str] = None
    provenance: Optional[Dict[str, Any]] = None  # {retriever, retrieval_timestamp, ranking_stage, fusion_stage}

class EvidenceResponse(BaseModel):
    answer: str
    confidence: str
    confidence_score: float
    sources: List[Dict[str, Any]]
    evidence: List[EvidenceNode]
    why_this_answer: List[str]
    supporting_modalities: List[str]
