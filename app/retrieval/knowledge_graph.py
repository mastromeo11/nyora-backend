from typing import List, Dict, Any
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.memory_models import ConversationTurn
from app.retrieval.entity_extractor import extract_entities_from_text
from app.retrieval.entity_alias_registry import normalize_entity_name

def build_knowledge_graph(
    evidence_list: List[Any] = None,
    session_id: str = "default_session",
    goal: Any = None,
    plan: Any = None,
    tasks: List[Any] = None,
    executed_tools: List[Any] = None,
    observations: List[Any] = None,
    reflections: List[Any] = None,
    trace: Any = None,
    turns: List[Any] = None,
    summaries: List[Dict[str, Any]] = None,
    semantic_relations: List[Any] = None,
    temporal_events: List[Any] = None
) -> Dict[str, Any]:
    """
    Builds the unified Knowledge Graph representation.
    Separately handles Structural Graph (execution/system mapping)
    and Semantic Graph (conceptual entities and verbal relationships)
    to prevent cross-contamination.
    """
    nodes = []
    edges = []
    existing_ids = set()
    
    # helper to add nodes safely
    def add_node(node_id: str, label: str, node_type: str, **kwargs):
        if node_id not in existing_ids:
            node_dict = {
                "id": node_id,
                "label": label,
                "type": node_type
            }
            node_dict.update(kwargs)
            nodes.append(node_dict)
            existing_ids.add(node_id)
            
    # helper to add edges safely
    def add_edge(source: str, target: str, edge_type: str, **kwargs):
        # Prevent loops and duplicates
        if source == target:
            return
        edge_id = f"{source}_{edge_type}_{target}"
        if edge_id not in existing_ids:
            edge_dict = {
                "source": source,
                "target": target,
                "type": edge_type
            }
            edge_dict.update(kwargs)
            edges.append(edge_dict)
            existing_ids.add(edge_id)

    # 1. Add Semantic Entities & Relations
    if semantic_relations:
        for rel in semantic_relations:
            # entities
            src = rel.source_entity
            tgt = rel.target_entity
            src_norm = normalize_entity_name(src)
            tgt_norm = normalize_entity_name(tgt)
            
            src_id = f"entity_{src_norm}"
            tgt_id = f"entity_{tgt_norm}"
            
            add_node(src_id, src.upper(), "entity", canonical_name=src_norm)
            add_node(tgt_id, tgt.upper(), "entity", canonical_name=tgt_norm)
            
            # semantic relationship edge
            add_edge(src_id, tgt_id, rel.relation_type, relation_id=rel.relation_id, weight=rel.weight)

    # 2. Add Temporal Events
    if temporal_events:
        for idx, event in enumerate(temporal_events):
            event_id = event.event_id
            add_node(
                event_id, 
                event.description, 
                "event_node", 
                event_type=event.event_type, 
                timestamp=event.timestamp
            )
            for ent in event.entities:
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                # edge: event to entity
                add_edge(event_id, ent_id, "event_to_entity")

    # 3. Add Structural Graph Objects (System/Process mappings)
    # A. Evidence Nodes
    if evidence_list:
        for node in evidence_list:
            if isinstance(node, dict):
                ev_id = node.get("evidence_id")
                source = node.get("source")
                content = node.get("content")
                modality = node.get("modality")
            else:
                ev_id = getattr(node, "evidence_id", None)
                source = getattr(node, "source", None)
                content = getattr(node, "content", None)
                modality = getattr(node, "modality", None)
                
            if ev_id:
                add_node(ev_id, source, "evidence", modality=modality, content=content)
                # Link to matching entities in content
                ents = extract_entities_from_text(content or "")
                for ent in ents:
                    ent_norm = normalize_entity_name(ent)
                    ent_id = f"entity_{ent_norm}"
                    add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                    # structural edge
                    add_edge(ent_id, ev_id, "entity_to_evidence")

    # B. Memory turns
    if turns:
        prev_turn_id = None
        for idx, turn in enumerate(turns):
            if isinstance(turn, dict):
                user_query = turn.get("user_query")
                assistant_answer = turn.get("assistant_answer")
                ts = turn.get("timestamp")
            else:
                user_query = getattr(turn, "user_query", "")
                assistant_answer = getattr(turn, "assistant_answer", "")
                ts = getattr(turn, "timestamp", "")
                
            turn_node_id = f"turn_{idx+1}"
            label = f"Turn {idx+1}: {user_query[:20]}..."
            add_node(turn_node_id, label, "turn_node", query=user_query, answer=assistant_answer, timestamp=ts)
            
            if prev_turn_id:
                add_edge(prev_turn_id, turn_node_id, "turn_to_turn")
            prev_turn_id = turn_node_id
            
            # Connect turns to mentioned entities
            ents = extract_entities_from_text(user_query + " " + assistant_answer)
            for ent in ents:
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                add_edge(turn_node_id, ent_id, "turn_to_entity")

    # C. Summaries
    if summaries:
        for idx, summ in enumerate(summaries):
            summary_node_id = f"summary_{idx+1}"
            text = summ.get("summary", "")
            add_node(summary_node_id, f"Summary {idx+1}", "summary_node", summary=text)
            for ent in summ.get("entity_focus", []):
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                add_edge(summary_node_id, ent_id, "summary_to_entity")

    # D. Agent components (Goal, Plan, Tasks, Tools, Obs, Reflections, Trace)
    if goal:
        if isinstance(goal, dict):
            g_id = goal.get("goal_id")
            g_type = goal.get("goal_type")
            g_query = goal.get("query")
        else:
            g_id = getattr(goal, "goal_id", None)
            g_type = getattr(goal, "goal_type", None)
            g_query = getattr(goal, "query", None)
            
        if g_id:
            goal_id = f"goal_{g_id}"
            add_node(goal_id, f"Goal: {g_type}", "goal_node", query=g_query)
            
            # Connect entity -> goal
            ents = extract_entities_from_text(g_query or "")
            for ent in ents:
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                add_edge(ent_id, goal_id, "entity_to_goal")
                
    if plan and goal:
        g_id = goal.get("goal_id") if isinstance(goal, dict) else getattr(goal, "goal_id", None)
        p_id = plan.get("plan_id") if isinstance(plan, dict) else getattr(plan, "plan_id", None)
        p_steps = plan.get("steps") if isinstance(plan, dict) else getattr(plan, "steps", [])
        
        if p_id and g_id:
            plan_id = f"plan_{p_id}"
            goal_id = f"goal_{g_id}"
            add_node(plan_id, f"Plan: {len(p_steps or [])} steps", "plan_node", steps=p_steps)
            add_edge(goal_id, plan_id, "goal_to_plan")
            
    if tasks and plan:
        p_id = plan.get("plan_id") if isinstance(plan, dict) else getattr(plan, "plan_id", None)
        if p_id:
            plan_id = f"plan_{p_id}"
            for idx, task in enumerate(tasks):
                if isinstance(task, dict):
                    t_id = task.get("task_id")
                    t_desc = task.get("description", "")
                    t_deps = task.get("dependency_ids") or []
                else:
                    t_id = getattr(task, "task_id", None)
                    t_desc = getattr(task, "description", "")
                    t_deps = getattr(task, "dependency_ids", None) or []
                    
                task_node_id = f"task_{t_id}"
                add_node(task_node_id, f"Task {t_id}", "task_node", description=t_desc)
                add_edge(plan_id, task_node_id, "plan_to_task")
                
                for dep in t_deps:
                    add_edge(f"task_{dep}", task_node_id, "task_dependency")
                    
                # Link entity -> task
                ents = extract_entities_from_text(t_desc)
                for ent in ents:
                    ent_norm = normalize_entity_name(ent)
                    ent_id = f"entity_{ent_norm}"
                    add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                    add_edge(ent_id, task_node_id, "entity_to_task")

    if executed_tools and tasks:
        for idx, tool in enumerate(executed_tools):
            t_name = tool.get("tool_name") if isinstance(tool, dict) else getattr(tool, "tool_name", f"tool_{idx}")
            tool_node_id = f"tool_{t_name}_{idx}"
            add_node(tool_node_id, f"Tool: {t_name}", "tool_node", tool_name=t_name)
            
            if idx < len(tasks):
                task_item = tasks[idx]
                t_id = task_item.get("task_id") if isinstance(task_item, dict) else getattr(task_item, "task_id", None)
                if t_id:
                    add_edge(f"task_{t_id}", tool_node_id, "task_to_tool")

    if observations and executed_tools:
        for idx, obs in enumerate(observations):
            o_id = obs.get("observation_id") if isinstance(obs, dict) else getattr(obs, "observation_id", f"obs_{idx}")
            content = obs.get("content") if isinstance(obs, dict) else getattr(obs, "content", "")
            obs_node_id = f"observation_{o_id}"
            add_node(obs_node_id, f"Observation {o_id}", "observation_node", content=content)
            
            # Connect tool -> observation
            if idx < len(executed_tools):
                tool_item = executed_tools[idx]
                t_name = tool_item.get("tool_name") if isinstance(tool_item, dict) else getattr(tool_item, "tool_name", f"tool_{idx}")
                add_edge(f"tool_{t_name}_{idx}", obs_node_id, "tool_to_observation")
                
            # Connect entity -> observation
            ents = extract_entities_from_text(content)
            for ent in ents:
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                add_edge(ent_id, obs_node_id, "entity_to_observation")

    if reflections and observations:
        for idx, refl in enumerate(reflections):
            r_id = refl.get("reflection_id") if isinstance(refl, dict) else getattr(refl, "reflection_id", f"refl_{idx}")
            reason = refl.get("reason") if isinstance(refl, dict) else getattr(refl, "reason", "")
            refl_node_id = f"reflection_{r_id}"
            add_node(refl_node_id, f"Reflection: {r_id}", "reflection_node", reason=reason)
            
            # Connect observation -> reflection
            if idx < len(observations):
                obs_item = observations[idx]
                o_id = obs_item.get("observation_id") if isinstance(obs_item, dict) else getattr(obs_item, "observation_id", f"obs_{idx}")
                add_edge(f"observation_{o_id}", refl_node_id, "observation_to_reflection")
                
            # Connect entity -> reflection
            ents = extract_entities_from_text(reason)
            for ent in ents:
                ent_norm = normalize_entity_name(ent)
                ent_id = f"entity_{ent_norm}"
                add_node(ent_id, ent.upper(), "entity", canonical_name=ent_norm)
                add_edge(ent_id, refl_node_id, "entity_to_reflection")

    if trace and goal and plan:
        t_id = trace.get("trace_id") if isinstance(trace, dict) else getattr(trace, "trace_id", None)
        g_id = goal.get("goal_id") if isinstance(goal, dict) else getattr(goal, "goal_id", None)
        p_id = plan.get("plan_id") if isinstance(plan, dict) else getattr(plan, "plan_id", None)
        
        if t_id and g_id and p_id:
            trace_id = f"trace_{t_id}"
            goal_id = f"goal_{g_id}"
            plan_id = f"plan_{p_id}"
            add_node(trace_id, f"Trace {t_id[:8]}", "trace_node")
            add_edge(goal_id, trace_id, "goal_to_trace")
            add_edge(plan_id, trace_id, "plan_to_trace")
            
            # Connect trace -> observation
            if observations:
                for idx, obs in enumerate(observations):
                    o_id = obs.get("observation_id") if isinstance(obs, dict) else getattr(obs, "observation_id", f"obs_{idx}")
                    add_edge(trace_id, f"observation_{o_id}", "trace_to_observation")

    return {
        "nodes": nodes,
        "edges": edges
    }
