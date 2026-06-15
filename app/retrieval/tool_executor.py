import time
from typing import Any, Dict, Tuple
from app.retrieval.agent_models import ToolNode
from app.retrieval.tool_registry import registry
from app.config import TOOL_TIMEOUT_SECONDS

def execute_agent_tool(tool_name: str, inputs: Dict[str, Any]) -> Tuple[Any, ToolNode]:
    """
    Executes a registered tool, timing its execution and catching exceptions.
    Returns a tuple of (tool_outputs, ToolNode).
    """
    tool = registry.get(tool_name)
    if not tool:
        print(f"[TOOL EXECUTOR] Tool not found: {tool_name}")
        node = ToolNode(
            tool_name=tool_name,
            execution_time=0.0,
            success=False
        )
        return {"error": "Tool not found"}, node

    t_start = time.time()
    success = False
    outputs = None
    retry_count = 0
    max_retries = 2
    
    # Bounded retry execution loop
    while retry_count <= max_retries:
        try:
            # Execute the tool with inputs
            outputs = tool.execute(**inputs)
            success = True
            break
        except Exception as e:
            print(f"[TOOL EXECUTOR] Attempt {retry_count + 1} failed for tool {tool_name}: {e}")
            retry_count += 1
            outputs = {"error": str(e)}
            
    t_end = time.time()
    execution_time = round(t_end - t_start, 4)
    
    node = ToolNode(
        tool_name=tool_name,
        execution_time=execution_time,
        success=success
    )
    
    return outputs, node
