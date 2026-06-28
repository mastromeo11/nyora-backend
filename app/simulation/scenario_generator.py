import uuid
from typing import List, Optional
from app.simulation.simulation_models import ScenarioNode
from app.simulation.simulation_store import append_scenario, get_scenarios
from app.config import MAX_SCENARIO_BRANCHES

def generate_scenario_branch(
    parent_state_id: str,
    summary: str,
    success_probability: float = 1.0,
    risk_score: float = 0.0,
    importance_score: float = 0.0,
    embedding: Optional[List[float]] = None
) -> Optional[ScenarioNode]:
    """
    Creates and records a branching scenario from a parent state.
    Limits children branches to MAX_SCENARIO_BRANCHES.
    """
    existing_scenarios = get_scenarios()
    
    # Check current branch count from this parent state
    parent_branches = [s for s in existing_scenarios if s.parent_state == parent_state_id]
    if len(parent_branches) >= MAX_SCENARIO_BRANCHES:
        print(f"[SCENARIO GENERATOR] Max scenario branches reached for parent {parent_state_id} (Limit: {MAX_SCENARIO_BRANCHES})")
        return None
        
    scenario_id = f"scen_{uuid.uuid4().hex[:8]}"
    node = ScenarioNode(
        scenario_id=scenario_id,
        parent_state=parent_state_id,
        child_states=[],
        summary=summary,
        success_probability=success_probability,
        risk_score=risk_score,
        importance_score=importance_score,
        embedding=embedding,
        reinforcement_score=1.0
    )
    
    append_scenario(node)
    
    # Update parent scenario's child list if parent state refers to another ScenarioNode
    for parent_scen in existing_scenarios:
        if parent_scen.scenario_id == parent_state_id:
            if scenario_id not in parent_scen.child_states:
                parent_scen.child_states.append(scenario_id)
                append_scenario(parent_scen)
                
    return node
