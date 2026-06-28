import uuid
from datetime import datetime
from app.simulation.simulation_models import FailureSimulationNode
from app.simulation.simulation_store import append_failure_simulation, get_failure_simulations

def record_failure_simulation(
    simulation_id: str,
    failure_type: str,
    tool_failures: list = None,
    agent_failures: list = None,
    timeout_events: int = 0,
    risk_score: float = 0.5
) -> FailureSimulationNode:
    """
    Logs or reinforces a FailureSimulationNode tracking unsuccessful simulation outcomes.
    """
    tool_failures = tool_failures or []
    agent_failures = agent_failures or []
    
    # Check if a matching failure simulation already exists (based on simulation_id and failure_type)
    existing_nodes = get_failure_simulations()
    match = None
    for node in existing_nodes:
        if node.simulation_id == simulation_id and node.failure_type == failure_type:
            match = node
            break
            
    now_str = datetime.utcnow().isoformat()
    if match:
        match.frequency += 1
        match.timeout_events += timeout_events
        # Merge tool/agent failure details
        match.tool_failures = list(set(match.tool_failures + tool_failures))
        match.agent_failures = list(set(match.agent_failures + agent_failures))
        # Recalculate risk score
        match.risk_score = 0.7 * match.risk_score + 0.3 * risk_score
        match.last_seen = now_str
        node_to_save = match
    else:
        node_to_save = FailureSimulationNode(
            failure_simulation_id=f"fail_sim_{uuid.uuid4().hex[:8]}",
            simulation_id=simulation_id,
            failure_type=failure_type,
            tool_failures=tool_failures,
            agent_failures=agent_failures,
            timeout_events=timeout_events,
            risk_score=risk_score,
            frequency=1,
            last_seen=now_str
        )
        
    append_failure_simulation(node_to_save)
    return node_to_save
