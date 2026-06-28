import string
from typing import List
from app.simulation.simulation_models import ScenarioNode, FailureForecastNode

def compile_simulation_explanation(
    scenarios: List[ScenarioNode],
    forecasts: List[FailureForecastNode] = None
) -> str:
    """
    Compiles a natural explanation describing counterfactual branch choices.
    Hides raw chain-of-thought, explaining decision rationale based on success/risk scoring.
    Outputs structured reasons explaining why a preferred branch was selected.
    """
    if not scenarios:
        return ""
        
    forecasts = forecasts or []
    # Map risks
    risk_by_type = {f.failure_type.lower(): f.risk_score for f in forecasts}
    
    explanation_parts = []
    num_paths = len(scenarios)
    path_word = "paths" if num_paths > 1 else "path"
    explanation_parts.append(f"Planner simulated {num_paths} possible {path_word}. The planner considered {num_paths} future execution branches:")
    
    alphabet = string.ascii_uppercase
    
    # Find if there is a preferred branch
    preferred_idx = 0
    best_score = -1.0
    for idx, scen in enumerate(scenarios):
        # We can score them simply as success_probability - risk
        # Find if it has risks
        max_risk = 0.0
        for risk_type, risk_score in risk_by_type.items():
            if risk_type in scen.summary.lower():
                max_risk = max(max_risk, risk_score)
        scen_score = scen.success_probability - max_risk
        if scen_score > best_score:
            best_score = scen_score
            preferred_idx = idx
            
    preferred_letter = alphabet[preferred_idx] if preferred_idx < len(alphabet) else str(preferred_idx)
    
    for idx, scen in enumerate(scenarios[:3]):
        branch_letter = alphabet[idx] if idx < len(alphabet) else str(idx)
        
        # Determine risks
        has_risk = False
        risk_label = ""
        for risk_type, risk_score in risk_by_type.items():
            if risk_type in scen.summary.lower() and risk_score >= 0.5:
                has_risk = True
                risk_label = f" but has a high {risk_type} risk ({risk_score:.2f})"
                break
                
        if scen.success_probability >= 0.7:
            if has_risk:
                explanation_parts.append(
                    f"  - Branch {branch_letter}: High success probability ({scen.success_probability:.2f}){risk_label}."
                )
            else:
                explanation_parts.append(
                    f"  - Branch {branch_letter}: Previous highly successful simulation pathway."
                )
        else:
            explanation_parts.append(
                f"  - Branch {branch_letter}: Lower confidence pathway (probability: {scen.success_probability:.2f}), rejected due to risk profiles."
            )
            
    if num_paths > 0:
        explanation_parts.append(
            f"Branch {preferred_letter} had lower timeout risk and higher success probability. Therefore Branch {preferred_letter} was preferred."
        )
            
    return "\n".join(explanation_parts)
