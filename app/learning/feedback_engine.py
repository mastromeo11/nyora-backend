import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.learning.learning_models import FeedbackNode
from app.learning.learning_store import append_feedback
from app.config import MIN_FEEDBACK_CONFIDENCE

def calculate_feedback_score(confidence_label: str, grounding_report: List[Dict[str, Any]], user_signal: float = 1.0) -> float:
    """
    Computes feedback score using:
    feedback_score = 0.4 * confidence + 0.3 * grounding_score + 0.3 * user_signal
    """
    # 1. Map confidence label to numeric score
    conf_lbl = str(confidence_label).lower()
    if "high" in conf_lbl:
        conf_score = 1.0
    elif "medium" in conf_lbl:
        conf_score = 0.6
    elif "low" in conf_lbl:
        conf_score = 0.3
    else:
        try:
            conf_score = float(confidence_label)
        except Exception:
            conf_score = 0.5
            
    # 2. Map grounding report to numeric score
    grounding_score = 1.0
    if grounding_report:
        statuses = [str(item.get("status", "")).lower() for item in grounding_report]
        if "refuted" in statuses:
            grounding_score = 0.0
        elif "unsupported" in statuses:
            grounding_score = 0.5

    # 3. Calculate final score
    score = 0.4 * conf_score + 0.3 * grounding_score + 0.3 * user_signal
    return round(max(0.0, min(score, 1.0)), 4)

def compile_and_store_feedback(
    query: str,
    answer: str,
    feedback_type: str,
    confidence_label: str,
    grounding_report: List[Dict[str, Any]],
    user_signal: float = 1.0
) -> FeedbackNode:
    """
    Compiles and appends a FeedbackNode to the continual learning store.
    """
    score = calculate_feedback_score(confidence_label, grounding_report, user_signal)
    
    node = FeedbackNode(
        feedback_id=f"fb_{uuid.uuid4().hex[:8]}",
        query=query,
        answer=answer,
        feedback_type=feedback_type,
        confidence=score,
        timestamp=datetime.utcnow().isoformat()
    )
    
    append_feedback(node)
    return node
