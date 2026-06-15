from app.retrieval.evidence_models import EvidenceNode

def map_modality_name(modality: str) -> str:
    mapping = {
        "text": "Document Chunk",
        "ocr": "Image OCR Text",
        "caption": "Ingestion Image Caption",
        "vqa": "Visual QA Answer",
        "audio": "Audio Transcript Segment",
        "image": "Visual Match"
    }
    return mapping.get(modality.lower(), "Other Modality")

def generate_citations(ranked_evidence: list[EvidenceNode]) -> list[dict]:
    """
    Generates unique, structured citations from the ranked evidence list.
    """
    citations = []
    seen = set()
    
    for node in ranked_evidence:
        # Map modality/evidence type
        modality_label = map_modality_name(node.modality)
        
        # Unique identifier
        key = (node.source, modality_label, node.modality)
        if key not in seen:
            seen.add(key)
            citations.append({
                "source": node.source,
                "modality": modality_label,
                "evidence_type": node.modality,
                "reason": node.citation_reason
            })
            
    return citations
