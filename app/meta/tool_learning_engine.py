import uuid
from datetime import datetime
from app.meta.meta_store import get_tools, append_tool
from app.meta.meta_models import ToolLearningNode
from app.config import (
    TOOL_SUCCESS_WEIGHT, TOOL_CONFIDENCE_WEIGHT, TOOL_LATENCY_WEIGHT,
    TOOL_RECENCY_WEIGHT, TOOL_IMPORTANCE_WEIGHT
)

def record_tool_execution(
    tool_name: str,
    success: bool,
    latency_ms: float,
    confidence: float = 1.0,
    importance_score: float = 1.0,
    is_timeout: bool = False
) -> ToolLearningNode:
    """
    Updates tool tracking statistics (frequency, success rate, failures, average latency)
    and persists the updated node in the store.
    """
    tools = get_tools()
    node = None
    for t in tools:
        if t.tool_name == tool_name:
            node = t
            break

    if node is None:
        node = ToolLearningNode(
            tool_id=f"tool_{uuid.uuid4().hex[:8]}",
            tool_name=tool_name,
            frequency=0,
            success_rate=1.0 if success else 0.0,
            latency_ms=latency_ms,
            confidence=confidence,
            importance_score=importance_score,
            last_used=datetime.utcnow().isoformat()
        )

    # Accumulate fields
    node.frequency += 1
    node.latency_ms = (node.latency_ms * (node.frequency - 1) + latency_ms) / node.frequency
    node.last_used = datetime.utcnow().isoformat()
    node.importance_score = importance_score

    # Track latency history and variance
    lat_history = getattr(node, "latency_history", None)
    if lat_history is None:
        lat_history = []
    lat_history.append(latency_ms)
    node.latency_history = lat_history

    if len(lat_history) > 1:
        mean_lat = sum(lat_history) / len(lat_history)
        node.latency_variance = sum((x - mean_lat) ** 2 for x in lat_history) / len(lat_history)
    else:
        node.latency_variance = 0.0

    if is_timeout:
        node.timeout_count = getattr(node, "timeout_count", 0) + 1
        node.failure_count = getattr(node, "failure_count", 0) + 1
        node.success_rate = (node.success_rate * (node.frequency - 1) + 0.0) / node.frequency
        node.confidence *= 0.8
    elif not success:
        node.failure_count = getattr(node, "failure_count", 0) + 1
        node.success_rate = (node.success_rate * (node.frequency - 1) + 0.0) / node.frequency
        node.confidence *= 0.8
    else:
        node.success_rate = (node.success_rate * (node.frequency - 1) + 1.0) / node.frequency
        node.confidence = 0.7 * node.confidence + 0.3 * confidence

    # Calculate timeout and failure rates
    node.timeout_rate = node.timeout_count / node.frequency
    node.failure_rate = node.failure_count / node.frequency

    # Calculate latency score (lower latency -> higher score)
    node.latency_score = 1.0 / (1.0 + node.latency_ms / 1000.0)

    append_tool(node)
    return node

def get_tool_score(node: ToolLearningNode) -> float:
    """
    Calculates dynamic tool score using Milestone 16 configuration weights.
    """
    try:
        last_used_dt = datetime.fromisoformat(node.last_used)
        delta_sec = (datetime.utcnow() - last_used_dt).total_seconds()
        recency = 1.0 / (1.0 + delta_sec / 3600.0)
    except Exception:
        recency = 1.0

    latency_score = node.latency_score if node.latency_score is not None else (1.0 / (1.0 + node.latency_ms / 1000.0))
    score = (
        TOOL_SUCCESS_WEIGHT * node.success_rate +
        TOOL_CONFIDENCE_WEIGHT * node.confidence +
        TOOL_LATENCY_WEIGHT * latency_score +
        TOOL_RECENCY_WEIGHT * recency +
        TOOL_IMPORTANCE_WEIGHT * node.importance_score
    )
    return min(max(score, 0.0), 1.0)
