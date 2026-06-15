from typing import List, Dict, Any, Optional

def handle_agent_failure(
    failed_agent_id: str,
    failure_type: str,
    original_task: Dict[str, Any],
    alternative_agents: List[str]
) -> dict:
    """
    Reroutes task execution to alternative agents when the primary agent fails.
    """
    print(f"[FAILURE ENGINE] Detected failure '{failure_type}' for agent '{failed_agent_id}' during task: {original_task.get('description', 'unnamed')}")
    
    from app.swarm.agent_monitor import record_agent_execution
    record_agent_execution(failed_agent_id, success=False, is_timeout=(failure_type == "timeout"))
    
    if not alternative_agents:
        return {
            "status": "failed",
            "message": f"Agent {failed_agent_id} failed and no alternative agents are available.",
            "recovery_action": "abort"
        }
        
    from app.swarm.load_balancer import select_best_agent
    try:
        chosen_alternative = select_best_agent(alternative_agents)
        return {
            "status": "recovered",
            "assigned_agent": chosen_alternative,
            "recovery_action": "reroute",
            "original_task": original_task
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Recovery failed due to: {e}",
            "recovery_action": "abort"
        }
