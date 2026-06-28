from datetime import datetime
from typing import List, Tuple
from app.simulation.simulation_models import ScenarioNode
from app.simulation.simulation_store import get_failure_forecasts

def calculate_safety_score(scenario: ScenarioNode) -> float:
    """
    Computes a safety score (1.0 - risk) based on failure forecast risk scores.
    """
    forecasts = get_failure_forecasts()
    # Check if any entities or keywords match scenario summary
    highest_risk = 0.0
    summary_words = set(scenario.summary.lower().split())
    
    for f in forecasts:
        # If failure type or related entities are mentioned in scenario
        type_matched = f.failure_type.lower() in scenario.summary.lower()
        entity_matched = any(ent.lower() in summary_words for ent in f.entities)
        
        if type_matched or entity_matched:
            highest_risk = max(highest_risk, f.risk_score)
            
    return max(0.0, 1.0 - highest_risk)

def score_scenario_branch(scenario: ScenarioNode, recency_override: float = None) -> float:
    """
    Formula:
        score = 0.25 * success_probability + 0.25 * confidence + 0.20 * importance + 0.15 * recency + 0.15 * safety
    """
    success_probability = scenario.success_probability
    
    # In ScenarioNode, confidence can be derived or defaults to reinforcement_score/frequency or 1.0
    confidence = min(1.0, max(0.0, scenario.reinforcement_score))
    
    importance = scenario.importance_score
    
    # Recency: Defaulting to 1.0 unless overridden
    recency = recency_override if recency_override is not None else 1.0
    
    # Safety Score
    safety = calculate_safety_score(scenario)
    
    score = (0.25 * success_probability +
             0.25 * confidence +
             0.20 * importance +
             0.15 * recency +
             0.15 * safety)
             
    return max(0.0, min(1.0, score))

def rank_scenario_branches(scenarios: List[ScenarioNode]) -> List[Tuple[ScenarioNode, float]]:
    """
    Scores and ranks scenario nodes in descending order of their branch scores.
    """
    scored = []
    for s in scenarios:
        score = score_scenario_branch(s)
        scored.append((s, score))
    # Sort descending
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored
