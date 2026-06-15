from app.retrieval.evidence_models import EvidenceNode

def generate_why_this_answer(ranked_evidence: list[EvidenceNode]) -> list[str]:
    """
    Generates human-readable justifications explaining which evidence sources
    and matching details led the system to synthesize the produced response.
    """
    reasons = []
    seen_reasons = set()
    
    for node in ranked_evidence:
        mod = node.modality.lower()
        src = node.source
        
        if mod == "ocr":
            msg = f"Matched OCR text from image '{src}'"
        elif mod == "text":
            msg = f"Matched document text from '{src}'"
        elif mod == "audio":
            msg = f"Matched speech segment transcript from audio '{src}'"
        elif mod == "vqa":
            msg = f"Visual QA extracted direct answer from image '{src}'"
        elif mod == "caption":
            msg = f"Ingestion caption describes visual contents of '{src}'"
        elif mod == "image":
            category = node.visual_category or "diagram"
            msg = f"Visual match classified as '{category}' retrieved through CLIP for '{src}'"
        else:
            msg = f"Semantic match of type '{mod}' found in '{src}'"
            
        if msg not in seen_reasons:
            seen_reasons.add(msg)
            reasons.append(msg)
            
    return reasons
