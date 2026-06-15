from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.source_quality import get_source_quality
from app.config import MAX_EVIDENCE_ITEMS
from app.retrieval.evidence_graph import extract_entities

def classify_query_intent(query: str) -> str:
    """
    Classifies search intent to build the QueryIntentProfile.
    """
    q = query.lower()
    visual_keywords = [
        "diagram", "flowchart", "dashboard", "image", "picture", 
        "screenshot", "mockup", "ui", "view", "graph", "chart", 
        "table", "bars", "circles", "nodes", "layout", "component", 
        "shown", "columns", "headers"
    ]
    audio_keywords = [
        "audio", "transcript", "speak", "sound", "call", "voice", 
        "speech", "recording", "meeting", "board", "spoken"
    ]
    
    has_visual = any(kw in q for kw in visual_keywords)
    has_audio = any(kw in q for kw in audio_keywords)
    
    if has_visual and has_audio:
        return "MULTIMODAL_BALANCED"
    elif has_visual:
        return "VISUAL_DOMINANT"
    elif has_audio:
        return "AUDIO_DOMINANT"
    else:
        return "TEXT_DOMINANT"

def rank_evidence(evidence_list: list[EvidenceNode], query: str) -> list[EvidenceNode]:
    """
    Dynamically ranks evidence nodes based on query-specific modality weighting.
    """
    intent = classify_query_intent(query)
    
    # Define query-intent profile weights
    if intent == "VISUAL_DOMINANT":
        text_w, visual_w, audio_w, quality_w = 0.20, 0.60, 0.10, 0.10
    elif intent == "AUDIO_DOMINANT":
        text_w, visual_w, audio_w, quality_w = 0.20, 0.10, 0.60, 0.10
    elif intent == "TEXT_DOMINANT":
        text_w, visual_w, audio_w, quality_w = 0.60, 0.15, 0.15, 0.10
    else:  # MULTIMODAL_BALANCED / fallback
        text_w, visual_w, audio_w, quality_w = 0.40, 0.30, 0.20, 0.10
        
    MIN_EVIDENCE_SCORE = 0.40
    TOP_K_PER_MODALITY = 2
    
    query_entities = extract_entities(query)
    
    filtered_evidence = []
    for node in evidence_list:
        semantic_sim = 0.0
        visual_conf = 0.0
        audio_conf = 0.0
        
        # Extract matching scores based on evidence modality type
        if node.modality in ["text", "ocr"]:
            semantic_sim = node.retrieval_score
        elif node.modality in ["image", "caption", "vqa"]:
            visual_conf = node.retrieval_score
        elif node.modality == "audio":
            audio_conf = node.retrieval_score
            
        quality_prior = get_source_quality(node.modality)
        
        # Calculate dynamic final score
        final_score = (
            text_w * semantic_sim +
            visual_w * visual_conf +
            audio_w * audio_conf +
            quality_w * quality_prior
        )
        
        # Recalibrate node properties
        node.retrieval_score = round(final_score, 4)
        node.confidence = "High" if final_score > 0.75 else ("Medium" if final_score > 0.50 else "Low")
        
        # Entity-based score boost to prevent filtering out relevant cross-modal nodes
        node_entities = extract_entities(node.content).union(extract_entities(node.source))
        n_lower = node.content.lower()
        
        has_entity_match = False
        for q_ent in query_entities:
            for n_ent in node_entities:
                if q_ent == n_ent:
                    has_entity_match = True
                elif "chroma" in q_ent and ("chromat" in n_lower or "chroma" in n_lower):
                    has_entity_match = True
                    
        if has_entity_match:
            final_score += 0.35
            node.retrieval_score = round(final_score, 4)
            node.confidence = "High" if final_score > 0.75 else ("Medium" if final_score > 0.50 else "Low")
            
        if node.provenance:
            node.provenance["ranking_stage"] = f"dynamic_ranked_{intent.lower()}"
            
        if node.retrieval_score >= MIN_EVIDENCE_SCORE:
            filtered_evidence.append(node)
            
    # Sort globally by score descending
    filtered_evidence.sort(key=lambda x: x.retrieval_score, reverse=True)
    
    # Cap to top-2 per modality
    capped_evidence = []
    modality_counts = {}
    for node in filtered_evidence:
        mod = node.modality.lower()
        count = modality_counts.get(mod, 0)
        if count < TOP_K_PER_MODALITY:
            capped_evidence.append(node)
            modality_counts[mod] = count + 1
            
    return capped_evidence[:MAX_EVIDENCE_ITEMS]
