from typing import List, Dict, Any
from app.meta.meta_models import (
    ToolLearningNode, PlannerPolicyNode, StrategyNode, MetaReflectionNode, PolicyReplayNode
)

def build_meta_graph(
    tools: List[ToolLearningNode],
    policies: List[PlannerPolicyNode],
    strategies: List[StrategyNode],
    reflections: List[MetaReflectionNode],
    replays: List[PolicyReplayNode]
) -> Dict[str, Any]:
    """
    Assembles a semantic meta-cognitive graph.
    Edges tracked:
    - ToolLearningNode -> PlannerPolicyNode
    - PlannerPolicyNode -> StrategyNode
    - StrategyNode -> PolicyReplayNode
    - MetaReflectionNode -> StrategyNode
    """
    nodes = []
    edges = []

    # Assemble nodes
    for t in tools:
        nodes.append({"id": t.tool_id, "type": "tool_learning", "name": t.tool_name})

    for p in policies:
        nodes.append({"id": p.policy_id, "type": "planner_policy", "planner_type": p.planner_type})

    for s in strategies:
        nodes.append({"id": s.strategy_id, "type": "strategy", "pattern": s.query_pattern})

    for r in reflections:
        nodes.append({"id": r.reflection_id, "type": "meta_reflection", "summary": r.reflection_summary})

    for rep in replays:
        nodes.append({
            "id": rep.replay_id,
            "type": "policy_replay",
            "source": rep.source_policy,
            "target": rep.target_policy
        })

    # ToolLearningNode -> PlannerPolicyNode
    for p in policies:
        for t in tools:
            if t.tool_name in p.signature or t.tool_name in p.policy_id:
                edges.append({
                    "source": t.tool_id,
                    "target": p.policy_id,
                    "type": "tool_to_policy"
                })

    # PlannerPolicyNode -> StrategyNode
    for p in policies:
        for s in strategies:
            if p.planner_type == s.planner_id:
                edges.append({
                    "source": p.policy_id,
                    "target": s.strategy_id,
                    "type": "policy_to_strategy"
                })

    # StrategyNode -> PolicyReplayNode
    for s in strategies:
        for rep in replays:
            if s.planner_id in rep.source_policy or s.planner_id in rep.target_policy:
                edges.append({
                    "source": s.strategy_id,
                    "target": rep.replay_id,
                    "type": "strategy_to_replay"
                })

    # MetaReflectionNode -> StrategyNode
    for r in reflections:
        for s in strategies:
            if r.query_signature in s.query_pattern:
                edges.append({
                    "source": r.reflection_id,
                    "target": s.strategy_id,
                    "type": "reflection_to_strategy"
                })

    return {"nodes": nodes, "edges": edges}
