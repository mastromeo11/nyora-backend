def calibrate_personality_confidence(
    historical_conf: float,
    historical_success: float,
    recent_success: float,
    recent_outcome: float,
    recency: float = 1.0
) -> float:
    """
    Calibrates confidence of personalization nodes using variance and consistency checks.
    Formula:
    consistency = 1 - |historical_success - recent_success|
    variance_penalty = 1 - |historical_success - recent_success|
    confidence = 0.35 * historical + 0.25 * recent + 0.20 * consistency + 0.10 * recency + 0.10 * variance_penalty
    """
    penalty = 1.0 - abs(historical_success - recent_success)
    consistency = penalty
    variance_penalty = penalty
    
    new_conf = (
        0.35 * historical_conf +
        0.25 * recent_outcome +
        0.20 * consistency +
        0.10 * recency +
        0.10 * variance_penalty
    )
    return min(max(new_conf, 0.0), 1.0)
