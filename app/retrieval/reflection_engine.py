import uuid
from datetime import datetime
from typing import Optional
from app.retrieval.agent_models import ToolNode, ObservationNode, ReflectionNode

def detect_and_reflect(tool_node: ToolNode, obs_node: ObservationNode) -> Optional[ReflectionNode]:
    """
    Analyzes a tool execution and its observation to detect failures.
    Returns a ReflectionNode if a failure is detected, else None.
    """
    failure_type = ""
    reason = ""
    
    # 1. Tool execution failure
    if not tool_node.success:
        failure_type = "TOOL_FAILURE"
        reason = f"Execution of tool {tool_node.tool_name} failed or timed out."
        
    # 2. Empty observations / Weak evidence
    elif "returned no evidence" in obs_node.content or "returned no results" in obs_node.content:
        failure_type = "EMPTY_OBSERVATION"
        reason = f"Tool {tool_node.tool_name} executed successfully but returned zero results."
        
    # 3. Failed simulation
    elif "failure sim" in obs_node.content.lower() or "simulated timeout" in obs_node.content.lower():
        failure_type = "SIMULATED_FAILURE"
        reason = f"Execution of tool {tool_node.tool_name} failed due to simulation."
        
    if failure_type:
        return ReflectionNode(
            reflection_id=f"refl_{uuid.uuid4().hex[:8]}",
            reason=reason,
            failure_type=failure_type,
            timestamp=datetime.utcnow().isoformat()
        )
        
    return None
