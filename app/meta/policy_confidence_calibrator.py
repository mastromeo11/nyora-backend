from typing import Optional

def calibrate_policy_confidence(
    historical_success: float,
    recent_success: float,
    recency: float,
    consistency: Optional[float] = None
) -> float:
    """
    Calibrates policy confidence to prevent confidence inflation:
    confidence = 0.4*historical_success + 0.3*recent_success + 0.2*consistency + 0.1*recency
    where consistency = 1 - abs(historical_success - recent_success)
    """
    if consistency is None:
        consistency = 1.0 - abs(historical_success - recent_success)

    confidence = (
        0.4 * historical_success +
        0.3 * recent_success +
        0.2 * consistency +
        0.1 * recency
    )
    return min(max(confidence, 0.0), 1.0)
