from app.config import HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD

def compute_visual_confidence(clip_score: float, ocr_confidence: float, vqa_valid: bool) -> str:
    """
    Calibrates visual QA retrieval confidence mapping:
    - Combines CLIP score, OCR detection confidence, and VQA response validity.
    - Standardizes into qualitative categories: High, Medium, Low.
    """
    score = clip_score
    
    # Adjust score dynamically based on OCR confidence and valid VQA groundedness
    if vqa_valid:
        score += 0.05
    else:
        score -= 0.10
        
    if ocr_confidence > 0.80:
        score += 0.05
        
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "High"
    elif score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "Medium"
    else:
        return "Low"
