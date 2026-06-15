from app.retrieval.text_retriever import retrieve_text
from app.retrieval.image_retriever import retrieve_images
from app.config import FUSION_TEXT_WEIGHT, FUSION_VISUAL_WEIGHT

def detect_query_intent(query: str) -> str:
    """
    Classifies the user search query intent into text-focused, visual-focused, or multimodal.
    """
    q = query.lower()
    visual_keywords = ["diagram", "flowchart", "dashboard", "image", "picture", "screenshot", "mockup", "ui", "view", "graph", "chart", "table"]
    text_keywords = ["what is", "how do", "explain", "why", "who", "definition", "describe", "summary", "list", "notes", "text"]
    
    has_visual = any(kw in q for kw in visual_keywords)
    has_text = any(kw in q for kw in text_keywords)
    
    if has_visual and has_text:
        return "multimodal"
    elif has_visual:
        return "visual-focused"
    else:
        return "text-focused"

def retrieve_multimodal(query: str, text_limit: int = 3, image_limit: int = 3) -> dict:
    """
    Executes intent detection and retrieves/fuses text and visual results.
    
    Args:
        query (str): The search query.
        text_limit (int): Max text chunks to retrieve.
        image_limit (int): Max image chunks to retrieve.
        
    Returns:
        dict: A structured dictionary containing fused results, individual results, and intent diagnostics.
    """
    # 1. Detect query intent
    intent = detect_query_intent(query)
    
    # 2. Adjust retrieval counts based on intent
    if intent == "text-focused":
        adjusted_text_limit = text_limit + 2
        adjusted_image_limit = max(image_limit - 1, 1)
    elif intent == "visual-focused":
        adjusted_text_limit = max(text_limit - 1, 1)
        adjusted_image_limit = image_limit + 2
    else:
        adjusted_text_limit = text_limit
        adjusted_image_limit = image_limit
        
    # 3. Retrieve raw candidates
    text_results = retrieve_text(query, n_results=adjusted_text_limit)
    image_results = retrieve_images(query, limit=adjusted_image_limit)
    
    # 4. Perform Multimodal Fusion Scoring
    # Map sources by filename
    sources_map = {}
    
    # Process text results
    for t_res in text_results:
        src = t_res["source"]
        if src not in sources_map:
            sources_map[src] = {"text": t_res, "image": None}
        else:
            sources_map[src]["text"] = t_res
            
    # Process image results
    for i_res in image_results:
        src = i_res["source"]
        if src not in sources_map:
            sources_map[src] = {"text": None, "image": i_res}
        else:
            sources_map[src]["image"] = i_res
            
    # Calculate fusion scores
    fused_candidates = []
    for src, match in sources_map.items():
        t_match = match["text"]
        i_match = match["image"]
        
        t_score = t_match["score"] if t_match else 0.0
        i_score = i_match["score"] if i_match else 0.0
        
        # Weighted fusion score formula
        fusion_score = (FUSION_TEXT_WEIGHT * t_score) + (FUSION_VISUAL_WEIGHT * i_score)
        
        # Retrieve explanation and details
        from app.retrieval.explanation_generator import generate_multimodal_explanation
        
        caption = None
        if i_match:
            caption = i_match["metadata"].get("caption", "A visual document.")
            
        # Populate merged details
        if t_match and i_match:
            source_type = "multimodal"
            confidence = "High" if fusion_score >= 0.55 else ("Medium" if fusion_score >= 0.45 else "Low")
            ocr_conf = i_match.get("ocr_confidence") or t_match.get("ocr_confidence")
            file_path = i_match.get("file_path")
            visual_category = i_match.get("visual_category")
            
            reason = generate_multimodal_explanation(t_score, i_score, visual_category)
            caption_str = f" [Image Caption: {caption}]" if caption else ""
            snippet = f"{t_match['text']}{caption_str} | Category: {visual_category} | Explanation: {reason}"
        elif t_match:
            source_type = t_match["source_type"] or "text"
            confidence = t_match["confidence"]
            ocr_conf = t_match.get("ocr_confidence")
            file_path = None
            visual_category = "document"
            reason = f"Text-only semantic match (BGE Score: {t_score:.4f}, Confidence: {confidence})."
            snippet = t_match["text"]
        else:
            source_type = "image"
            confidence = i_match["confidence"]
            ocr_conf = i_match.get("ocr_confidence")
            file_path = i_match.get("file_path")
            visual_category = i_match.get("visual_category")
            
            reason = generate_multimodal_explanation(0.0, i_score, visual_category)
            caption_str = f" Caption: {caption}." if caption else ""
            ocr_text = i_match["metadata"].get("text", "")
            ocr_str = f" OCR Text: {ocr_text}" if ocr_text else " OCR text was empty."
            snippet = f"[Visual Document] Category: {visual_category}.{caption_str}{ocr_str} | Explanation: {reason}"
            
        fused_candidates.append({
            "source": src,
            "source_type": source_type,
            "score": fusion_score,
            "confidence": confidence,
            "text": snippet,
            "file_path": file_path,
            "ocr_confidence": ocr_conf,
            "visual_category": visual_category,
            "retrieved_reason": reason,
            "caption": caption,
            "details": {
                "text_score": t_score,
                "visual_score": i_score
            }
        })
        
    # Sort fused results by score descending
    fused_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Apply final limit
    final_limit = max(text_limit, image_limit)
    fused_results = fused_candidates[:final_limit]
    
    return {
        "query_intent": intent,
        "fused_results": fused_results,
        "text_results": text_results[:text_limit],
        "image_results": image_results[:image_limit]
    }
