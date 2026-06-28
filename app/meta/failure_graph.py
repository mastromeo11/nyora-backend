from typing import List, Dict, Any
from app.meta.meta_models import ToolFailureNode, PolicyFailureNode, ReflectionFailureNode, OptimizationFailureNode

def build_meta_failure_graph(
    tool_failures: List[ToolFailureNode],
    policy_failures: List[PolicyFailureNode],
    reflection_failures: List[ReflectionFailureNode],
    optimization_failures: List[OptimizationFailureNode] = []
) -> Dict[str, Any]:
    """
    Constructs an isolated failure graph from failures of tools, policies, reflections, and optimizations.
    This graph does not connect to successful policy trees.
    """
    nodes = []
    edges = []

    # 1. Add nodes
    for tf in tool_failures:
        nodes.append({
            "id": tf.failure_id,
            "type": "tool_failure",
            "name": tf.tool_name,
            "failure_type": tf.failure_type,
            "frequency": tf.frequency,
            "last_seen": tf.last_seen
        })

    for pf in policy_failures:
        nodes.append({
            "id": pf.failure_id,
            "type": "policy_failure",
            "policy_id": pf.policy_id,
            "failure_reason": pf.failure_reason,
            "frequency": pf.frequency,
            "last_seen": pf.last_seen
        })

    for rf in reflection_failures:
        nodes.append({
            "id": rf.failure_id,
            "type": "reflection_failure",
            "reflection_id": rf.reflection_id,
            "failure_type": rf.failure_type,
            "frequency": rf.frequency,
            "last_seen": rf.last_seen
        })

    for of in optimization_failures:
        nodes.append({
            "id": of.failure_id,
            "type": "optimization_failure",
            "query": of.query,
            "failure_reason": of.failure_reason,
            "frequency": of.frequency,
            "last_seen": of.last_seen
        })

    # 2. Add edges (only within failure components)
    for pf in policy_failures:
        for tf in tool_failures:
            if tf.tool_name in pf.failure_reason:
                edges.append({
                    "source": tf.failure_id,
                    "target": pf.failure_id,
                    "type": "tool_failure_to_policy_failure"
                })

    for rf in reflection_failures:
        for pf in policy_failures:
            if pf.policy_id in rf.reflection_id or pf.policy_id in rf.failure_type:
                edges.append({
                    "source": pf.failure_id,
                    "target": rf.failure_id,
                    "type": "policy_failure_to_reflection_failure"
                })

    for of in optimization_failures:
        for pf in policy_failures:
            if pf.policy_id in of.failure_reason:
                edges.append({
                    "source": pf.failure_id,
                    "target": of.failure_id,
                    "type": "policy_failure_to_optimization_failure"
                })

    return {"nodes": nodes, "edges": edges}
