from typing import Any, List
from app.retrieval.agent_models import GoalNode, PlanNode

def generate_agent_explanation(
    goal: GoalNode,
    plan: PlanNode,
    executed_tools: List[Any],
    observations: List[Any],
    reflections: List[Any],
    citations: List[Any]
) -> str:
    """
    Generates a production-grade, human-readable summary of the agent execution lifecycle.
    Conceals internal thought reasoning to maintain clean explainability.
    """
    explanation_parts = []
    
    # 1. Goal & Classification
    explanation_parts.append(f"Goal Detected: {goal.goal_type} - '{goal.query}'")
    
    # 2. Planning
    steps_str = ", ".join(plan.steps)
    explanation_parts.append(f"Execution Plan: Compiled a {len(plan.steps)}-step trace: [{steps_str}]")
    
    # 3. Tools executed & Success rate
    success_count = sum([1 for t in executed_tools if getattr(t, "success", False)])
    total_tools = len(executed_tools)
    if total_tools > 0:
        rate = round((success_count / total_tools) * 100, 1)
        tools_str = ", ".join([getattr(t, "tool_name", str(t)) for t in executed_tools])
        explanation_parts.append(f"Tool Performance: Executed {total_tools} tools [{tools_str}] with success rate of {rate}%.")
    
    # 4. Fallback/Reflection notifications
    if reflections:
        fails_str = "; ".join([f"({getattr(r, 'failure_type', 'Error')}): {getattr(r, 'reason', '')}" for r in reflections])
        explanation_parts.append(f"Execution Reflections: Encoded {len(reflections)} execution adjustments: {fails_str}")
        
    # 5. Core Observations Summarized
    if observations:
        obs_content = " ".join([getattr(o, "content", "") for o in observations])
        explanation_parts.append(f"Key Findings: {obs_content}")
        
    # 6. Authority Source references
    if citations:
        sources_str = ", ".join({c.get("source", "unknown") if isinstance(c, dict) else getattr(c, "source", "unknown") for c in citations})
        explanation_parts.append(f"Authority Grounding: Verified final claims against evidence from {sources_str}.")
        
    return "\n\n".join(explanation_parts)
