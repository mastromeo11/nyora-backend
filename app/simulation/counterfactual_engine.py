import uuid
from app.simulation.simulation_models import CounterfactualNode
from app.simulation.simulation_store import append_counterfactual, get_counterfactuals
from app.simulation.counterfactual_validator import validate_counterfactual

def create_counterfactual(
    base_scenario: str,
    modified_variable: str,
    old_value: str,
    new_value: str,
    alternative_outcome: str,
    risk_delta: float = 0.0,
    confidence: float = 1.0
) -> CounterfactualNode:
    """
    Creates or registers a CounterfactualNode representing alternative trajectories.
    """
    existing = get_counterfactuals()
    match = None
    for c in existing:
        if (c.base_scenario == base_scenario and 
            c.modified_variable == modified_variable and 
            c.new_value == new_value):
            match = c
            break
            
    if match:
        match.alternative_outcome = alternative_outcome
        match.risk_delta = 0.7 * match.risk_delta + 0.3 * risk_delta
        match.confidence = 0.7 * match.confidence + 0.3 * confidence
        node_to_save = match
    else:
        node_to_save = CounterfactualNode(
            counterfactual_id=f"cf_{uuid.uuid4().hex[:8]}",
            base_scenario=base_scenario,
            modified_variable=modified_variable,
            old_value=old_value,
            new_value=new_value,
            alternative_outcome=alternative_outcome,
            risk_delta=risk_delta,
            confidence=confidence
        )
        
    if not validate_counterfactual(node_to_save):
        raise ValueError("Invalid counterfactual state transaction")
        
    append_counterfactual(node_to_save)
    return node_to_save
