from typing import List, Dict, Any
from app.retrieval.memory_graph import build_memory_graph

def build_agent_graph(
    evidence_list: List[Any],
    session_id: str,
    goal: Any = None,
    plan: Any = None,
    tasks: List[Any] = None,
    executed_tools: List[Any] = None,
    observations: List[Any] = None,
    reflections: List[Any] = None,
    trace: Any = None
) -> Dict[str, Any]:
    """
    Extends the conversation memory graph with agent nodes and edges.
    Connects:
    - goal -> plan
    - plan -> task
    - task -> tool
    - tool -> observation
    - observation -> reflection
    - observation -> evidence
    Supports both dict and model object types for nodes (crucial for cache deserialization).
    """
    # 1. Start with the conversation memory graph
    graph = build_memory_graph(evidence_list, session_id)
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    existing_ids = {node["id"] for node in nodes}
    
    # 2. Add Goal Node
    if goal:
        if isinstance(goal, dict):
            g_id = goal.get("goal_id")
            g_type = goal.get("goal_type")
            g_query = goal.get("query")
            g_timestamp = goal.get("timestamp")
        else:
            g_id = getattr(goal, "goal_id", None)
            g_type = getattr(goal, "goal_type", None)
            g_query = getattr(goal, "query", None)
            g_timestamp = getattr(goal, "timestamp", None)
            
        if g_id:
            goal_id = f"goal_{g_id}"
            if goal_id not in existing_ids:
                nodes.append({
                    "id": goal_id,
                    "label": f"Goal: {g_type}",
                    "type": "goal_node",
                    "query": g_query,
                    "timestamp": g_timestamp
                })
                existing_ids.add(goal_id)
            
    # 3. Add Plan Node
    if plan and goal:
        if isinstance(goal, dict):
            g_id = goal.get("goal_id")
        else:
            g_id = getattr(goal, "goal_id", None)
            
        if isinstance(plan, dict):
            p_id = plan.get("plan_id")
            p_steps = plan.get("steps") or []
            p_status = plan.get("status")
        else:
            p_id = getattr(plan, "plan_id", None)
            p_steps = getattr(plan, "steps", None) or []
            p_status = getattr(plan, "status", None)
            
        if p_id and g_id:
            plan_id = f"plan_{p_id}"
            goal_id = f"goal_{g_id}"
            if plan_id not in existing_ids:
                nodes.append({
                    "id": plan_id,
                    "label": f"Plan: {len(p_steps)} steps",
                    "type": "plan_node",
                    "steps": p_steps,
                    "status": p_status
                })
                existing_ids.add(plan_id)
                
            # Edge: goal -> plan
            edges.append({
                "source": goal_id,
                "target": plan_id,
                "type": "goal_to_plan"
            })
        
    # 4. Add Task Nodes
    if tasks and plan:
        if isinstance(plan, dict):
            p_id = plan.get("plan_id")
        else:
            p_id = getattr(plan, "plan_id", None)
            
        if p_id:
            plan_id = f"plan_{p_id}"
            for idx, task in enumerate(tasks):
                if isinstance(task, dict):
                    t_id = task.get("task_id") or f"task_{idx}"
                    t_desc = task.get("description") or ""
                    t_status = task.get("status")
                    t_deps = task.get("dependency_ids") or []
                else:
                    t_id = getattr(task, "task_id", None) or f"task_{idx}"
                    t_desc = getattr(task, "description", None) or ""
                    t_status = getattr(task, "status", None)
                    t_deps = getattr(task, "dependency_ids", None) or []
                    
                task_node_id = f"task_{t_id}"
                
                if task_node_id not in existing_ids:
                    nodes.append({
                        "id": task_node_id,
                        "label": f"Task: {t_desc[:30]}...",
                        "type": "task_node",
                        "description": t_desc,
                        "status": t_status
                    })
                    existing_ids.add(task_node_id)
                    
                # Edge: plan -> task
                edges.append({
                    "source": plan_id,
                    "target": task_node_id,
                    "type": "plan_to_task"
                })
                
                # Edges for task dependencies
                for dep_id in t_deps:
                    dep_node_id = f"task_{dep_id}"
                    edges.append({
                        "source": dep_node_id,
                        "target": task_node_id,
                        "type": "task_dependency"
                    })
                
    # 5. Add Tool Nodes
    if executed_tools and tasks:
        # We can map each tool node to the task it completed
        for idx, tool in enumerate(executed_tools):
            if isinstance(tool, dict):
                t_name = tool.get("tool_name") or f"tool_{idx}"
                t_success = tool.get("success", False)
                t_time = tool.get("execution_time", 0.0)
            else:
                t_name = getattr(tool, "tool_name", None) or f"tool_{idx}"
                t_success = getattr(tool, "success", False)
                t_time = getattr(tool, "execution_time", 0.0)
                
            tool_node_id = f"tool_{t_name}_{idx}"
            
            if tool_node_id not in existing_ids:
                nodes.append({
                    "id": tool_node_id,
                    "label": f"Tool: {t_name}",
                    "type": "tool_node",
                    "success": t_success,
                    "execution_time": t_time
                })
                existing_ids.add(tool_node_id)
                
            # Connect task to tool
            if idx < len(tasks):
                task_item = tasks[idx]
                if isinstance(task_item, dict):
                    t_id = task_item.get("task_id") or f"task_{idx}"
                else:
                    t_id = getattr(task_item, "task_id", None) or f"task_{idx}"
                task_node_id = f"task_{t_id}"
                edges.append({
                    "source": task_node_id,
                    "target": tool_node_id,
                    "type": "task_to_tool"
                })
                
    # 6. Add Observation Nodes
    if observations and executed_tools:
        for idx, obs in enumerate(observations):
            if isinstance(obs, dict):
                o_id = obs.get("observation_id") or f"obs_{idx}"
                o_content = obs.get("content") or ""
                o_ts = obs.get("timestamp")
            else:
                o_id = getattr(obs, "observation_id", None) or f"obs_{idx}"
                o_content = getattr(obs, "content", None) or ""
                o_ts = getattr(obs, "timestamp", None)
                
            obs_node_id = f"observation_{o_id}"
            
            if obs_node_id not in existing_ids:
                nodes.append({
                    "id": obs_node_id,
                    "label": f"Obs: {o_content[:30]}...",
                    "type": "observation_node",
                    "content": o_content,
                    "timestamp": o_ts
                })
                existing_ids.add(obs_node_id)
                
            # Connect tool to observation
            if idx < len(executed_tools):
                tool_item = executed_tools[idx]
                if isinstance(tool_item, dict):
                    t_name = tool_item.get("tool_name") or f"tool_{idx}"
                else:
                    t_name = getattr(tool_item, "tool_name", None) or f"tool_{idx}"
                tool_node_id = f"tool_{t_name}_{idx}"
                edges.append({
                    "source": tool_node_id,
                    "target": obs_node_id,
                    "type": "tool_to_observation"
                })
                
            # Connect observation to evidence nodes retrieved
            for node in evidence_list:
                if isinstance(node, dict):
                    node_id = node.get("evidence_id") or f"evidence_{idx}"
                else:
                    node_id = getattr(node, "evidence_id", None) or f"evidence_{idx}"
                edges.append({
                    "source": obs_node_id,
                    "target": node_id,
                    "type": "observation_to_evidence"
                })
                
    # 7. Add Reflection Nodes
    if reflections and observations:
        for idx, refl in enumerate(reflections):
            if isinstance(refl, dict):
                r_id = refl.get("reflection_id") or f"refl_{idx}"
                r_type = refl.get("failure_type") or "Error"
                r_reason = refl.get("reason") or ""
                r_ts = refl.get("timestamp")
            else:
                r_id = getattr(refl, "reflection_id", None) or f"refl_{idx}"
                r_type = getattr(refl, "failure_type", None) or "Error"
                r_reason = getattr(refl, "reason", None) or ""
                r_ts = getattr(refl, "timestamp", None)
                
            refl_node_id = f"reflection_{r_id}"
            
            if refl_node_id not in existing_ids:
                nodes.append({
                    "id": refl_node_id,
                    "label": f"Reflection: {r_type}",
                    "type": "reflection_node",
                    "reason": r_reason,
                    "timestamp": r_ts
                })
                existing_ids.add(refl_node_id)
                
            # Connect observation to reflection
            if idx < len(observations):
                obs_item = observations[idx]
                if isinstance(obs_item, dict):
                    o_id = obs_item.get("observation_id") or f"obs_{idx}"
                else:
                    o_id = getattr(obs_item, "observation_id", None) or f"obs_{idx}"
                obs_node_id = f"observation_{o_id}"
                edges.append({
                    "source": obs_node_id,
                    "target": refl_node_id,
                    "type": "observation_to_reflection"
                })
                
    # 8. Add Trace Node
    if trace and goal and plan:
        if isinstance(trace, dict):
            t_id = trace.get("trace_id")
            t_success = trace.get("success", True)
        else:
            t_id = getattr(trace, "trace_id", None)
            t_success = getattr(trace, "success", True)
            
        if isinstance(goal, dict):
            g_id = goal.get("goal_id")
        else:
            g_id = getattr(goal, "goal_id", None)
            
        if isinstance(plan, dict):
            p_id = plan.get("plan_id")
        else:
            p_id = getattr(plan, "plan_id", None)
            
        if t_id and g_id and p_id:
            trace_id = f"trace_{t_id}"
            goal_id = f"goal_{g_id}"
            plan_id = f"plan_{p_id}"
            
            if trace_id not in existing_ids:
                nodes.append({
                    "id": trace_id,
                    "label": f"Trace {t_id[:8]}",
                    "type": "trace_node",
                    "success": t_success
                })
                existing_ids.add(trace_id)
                
            # Connect trace to goal and plan
            edges.append({
                "source": goal_id,
                "target": trace_id,
                "type": "goal_to_trace"
            })
            edges.append({
                "source": plan_id,
                "target": trace_id,
                "type": "plan_to_trace"
            })
            
    return {
        "nodes": nodes,
        "edges": edges
    }
