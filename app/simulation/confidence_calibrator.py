from typing import Optional

def calibrate_confidence(historical_success: float, recent_success: float, consistency: Optional[float] = None, recency: float = 1.0) -> float:
    """
    Calibrates confidence values based on:
    0.4 * historical_success + 0.3 * recent_success + 0.2 * consistency + 0.1 * recency
    Consistency represents the similarity between historical and recent outcomes, penalizing high variance.
    If consistency is not provided, it is computed as 1.0 - abs(historical_success - recent_success).
    """
    if consistency is None:
        consistency = 1.0 - abs(historical_success - recent_success)
    
    val = 0.4 * historical_success + 0.3 * recent_success + 0.2 * consistency + 0.1 * recency
    # Bound it between 0.0 and 1.0
    return max(0.0, min(1.0, val))
