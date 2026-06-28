import uuid
from datetime import datetime
from app.meta.meta_store import get_tool_failures, append_tool_failure
from app.meta.meta_models import ToolFailureNode

def record_tool_failure(tool_name: str, failure_type: str) -> ToolFailureNode:
    """
    Records tool failure metrics. This data is strictly isolated
    and never modifies successful ToolLearningNode metrics or reinforces confidence.
    """
    failures = get_tool_failures()
    node = None
    for f in failures:
        if f.tool_name == tool_name and f.failure_type == failure_type:
            node = f
            break

    if node is None:
        node = ToolFailureNode(
            failure_id=f"tf_{uuid.uuid4().hex[:8]}",
            tool_name=tool_name,
            failure_type=failure_type,
            frequency=0,
            last_seen=datetime.utcnow().isoformat()
        )

    node.frequency += 1
    node.last_seen = datetime.utcnow().isoformat()

    append_tool_failure(node)
    return node
