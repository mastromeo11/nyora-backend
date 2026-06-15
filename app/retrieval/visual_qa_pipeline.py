import os
from datetime import datetime
from app.config import (
    VQA_MIN_SCORE,
    VISION_MODEL,
    MAX_VQA_CANDIDATES,
    ENABLE_MULTI_IMAGE_REASONING,
    ENABLE_EXPLANATIONS,
    ENABLE_VISUAL_CITATIONS
)
from app.retrieval.image_retriever import retrieve_images
from app.retrieval.confidence_utils import compute_visual_confidence
from app.retrieval.explanation_generator import generate_visual_explanation

def answer_visual_question(question: str) -> dict:
    """
    Executes VQA pipeline by retrieving candidate images via CLIP,
    running LLaVA sequentially, and selecting the first successful grounded answer.
    """
    # 1. Determine K visual candidates to evaluate based on config
    limit_k = MAX_VQA_CANDIDATES if ENABLE_MULTI_IMAGE_REASONING else 1
    candidates = retrieve_images(question, limit=limit_k, min_score=VQA_MIN_SCORE)
    
    all_candidates_debug = []
    selected_candidate = None
    final_answer = "The information is not visible in the image."
    selected_rank = 1
    
    # 2. Sequential VQA reasoning loop
    from app.llm.vision_client import ask_image_question
    
    for idx, cand in enumerate(candidates):
        image_path = cand["file_path"]
        source = cand["source"]
        clip_score = cand["score"]
        category = cand["visual_category"]
        caption = cand["metadata"].get("caption", "A visual document.")
        
        # Call VLM ask_image_question (checks and stores in local cache)
        ans = ask_image_question(image_path, question)
        
        all_candidates_debug.append({
            "candidate_rank": idx + 1,
            "candidate_source": source,
            "candidate_score": clip_score,
            "candidate_answer": ans,
            "file_path": image_path,
            "visual_category": category,
            "caption": caption
        })
        
        # Select first grounded (non-fallback) answer
        if selected_candidate is None and ans != "The information is not visible in the image.":
            selected_candidate = cand
            final_answer = ans
            selected_rank = idx + 1
            
    # Default to top matching candidate if VLM returned no answers
    if not selected_candidate and candidates:
        selected_candidate = candidates[0]
        selected_rank = 1
        
    # 3. Citation and Confidence Calibration
    if selected_candidate:
        source_image = selected_candidate["source"]
        file_path = selected_candidate["file_path"]
        visual_category = selected_candidate["visual_category"]
        caption = selected_candidate["metadata"].get("caption", "A visual document.")
        clip_score = selected_candidate["score"]
        ocr_conf = selected_candidate.get("ocr_confidence") or 0.0
        vqa_valid = (final_answer != "The information is not visible in the image.")
        
        confidence = compute_visual_confidence(
            clip_score=clip_score,
            ocr_confidence=ocr_conf,
            vqa_valid=vqa_valid
        )
        
        citation_reason = generate_visual_explanation(
            clip_score=clip_score,
            visual_category=visual_category,
            is_fallback=(not vqa_valid),
            selected_rank=selected_rank
        )
    else:
        source_image = None
        file_path = None
        visual_category = None
        caption = None
        clip_score = 0.0
        confidence = "Low"
        citation_reason = "No candidate images matched the query criteria."
        vqa_valid = False
        
    # Build returned payload
    response = {
        "question": question,
        "answer": final_answer,
        "source_image": source_image,
        "file_path": file_path,
        "visual_category": visual_category,
        "caption": caption,
        "clip_score": clip_score,
        "confidence": confidence,
        "model_used": VISION_MODEL,
        "timestamp": datetime.utcnow().isoformat(),
        "all_candidate_scores": [c["score"] for c in candidates],
        "all_candidates": all_candidates_debug
    }
    
    if ENABLE_VISUAL_CITATIONS:
        response["citation_reason"] = citation_reason
        
    return response

