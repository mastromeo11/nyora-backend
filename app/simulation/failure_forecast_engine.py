import uuid
from typing import List
from app.simulation.simulation_models import FailureForecastNode
from app.simulation.simulation_store import append_failure_forecast, get_failure_forecasts

def generate_failure_forecast(
    failure_type: str,
    history_score: float = 0.5,
    similarity_score: float = 0.5,
    recency_score: float = 1.0,
    frequency_val: int = 1,
    entities: List[str] = None
) -> FailureForecastNode:
    """
    Creates or updates a FailureForecastNode.
    Risk score formula:
        0.4 * history_score + 0.3 * similarity_score + 0.2 * recency_score + 0.1 * frequency_normalized
    """
    entities = entities or []
    
    # Check if failure forecast node with failure_type already exists
    existing = get_failure_forecasts()
    match = None
    for f in existing:
        if f.failure_type == failure_type:
            match = f
            break
            
    frequency_normalized = min(1.0, frequency_val / 10.0)
    risk_score = 0.4 * history_score + 0.3 * similarity_score + 0.2 * recency_score + 0.1 * frequency_normalized
    risk_score = max(0.0, min(1.0, risk_score))
    
    if match:
        match.risk_score = 0.7 * match.risk_score + 0.3 * risk_score
        match.probability = match.risk_score
        match.entities = list(set(match.entities + entities))
        node_to_save = match
    else:
        node_to_save = FailureForecastNode(
            failure_forecast_id=f"fail_fore_{uuid.uuid4().hex[:8]}",
            failure_type=failure_type,
            risk_score=risk_score,
            probability=risk_score,
            entities=entities
        )
        
    append_failure_forecast(node_to_save)
    return node_to_save
