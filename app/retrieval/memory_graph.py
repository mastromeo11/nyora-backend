from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.evidence_graph import build_evidence_graph, get_node_entities
from app.retrieval.session_memory import get_session
from app.retrieval.memory_cache import get_session_cache

def build_memory_graph(evidence_list: list, session_id: str) -> dict:
    """
    Extends the Evidence Graph with conversational memory components (turns, summaries, preferences).
    Returns a dictionary of nodes and edges.
    """
    # 1. Start with the base evidence graph
    base_graph = build_evidence_graph(evidence_list)
    nodes = base_graph["nodes"]
    edges = base_graph["edges"]
    
    # Track existing node IDs to avoid duplicates
    existing_ids = {node["id"] for node in nodes}
    
    # 2. Get history from session
    turns = get_session(session_id)
    session_data = get_session_cache(session_id)
    summaries = session_data.get("summaries", [])
    prefs = session_data.get("preference_memory", {})
    
    # 3. Add Turn Nodes and edges
    previous_turn_id = None
    for idx, turn in enumerate(turns):
        turn_node_id = f"turn_{idx+1}"
        label = f"Turn {idx+1}: {turn.user_query[:30]}..." if len(turn.user_query) > 30 else f"Turn {idx+1}: {turn.user_query}"
        
        if turn_node_id not in existing_ids:
            nodes.append({
                "id": turn_node_id,
                "label": label,
                "type": "turn_node",
                "query": turn.user_query,
                "answer": turn.assistant_answer,
                "timestamp": turn.timestamp
            })
            existing_ids.add(turn_node_id)
            
        # Connect consecutive turns
        if previous_turn_id:
            edges.append({
                "source": previous_turn_id,
                "target": turn_node_id,
                "type": "turn_to_turn"
            })
        previous_turn_id = turn_node_id
        
        # Connect Turn to Entities mentioned in that turn
        turn_ents = get_node_entities(turn.user_query).union(get_node_entities(turn.assistant_answer))
        for ent in turn_ents:
            entity_node_id = f"entity_{ent}"
            # Ensure entity node exists in graph
            if entity_node_id not in existing_ids:
                nodes.append({
                    "id": entity_node_id,
                    "label": ent.upper(),
                    "type": "entity"
                })
                existing_ids.add(entity_node_id)
                
            edges.append({
                "source": turn_node_id,
                "target": entity_node_id,
                "type": "turn_to_entity"
            })
            
    # 4. Add Summary Nodes and edges
    for idx, summ in enumerate(summaries):
        summary_node_id = f"summary_{idx+1}"
        summary_text = summ.get("summary", "")
        label = f"Summary {idx+1}: {summary_text[:30]}..." if len(summary_text) > 30 else f"Summary {idx+1}: {summary_text}"
        
        if summary_node_id not in existing_ids:
            nodes.append({
                "id": summary_node_id,
                "label": label,
                "type": "summary_node",
                "summary": summary_text,
                "timestamp": summ.get("timestamp")
            })
            existing_ids.add(summary_node_id)
            
        # Connect Summary to Entities featured in the summary's focus
        focus_ents = summ.get("entity_focus", [])
        for ent in focus_ents:
            entity_node_id = f"entity_{ent}"
            if entity_node_id not in existing_ids:
                nodes.append({
                    "id": entity_node_id,
                    "label": ent.upper(),
                    "type": "entity"
                })
                existing_ids.add(entity_node_id)
                
            edges.append({
                "source": summary_node_id,
                "target": entity_node_id,
                "type": "summary_to_entity"
            })
            
    # 5. Add Preference Nodes
    for key, val in prefs.items():
        pref_node_id = f"preference_{key}"
        label = f"Pref: {key}={val}"
        
        if pref_node_id not in existing_ids:
            nodes.append({
                "id": pref_node_id,
                "label": label,
                "type": "preference_node",
                "key": key,
                "value": val
            })
            existing_ids.add(pref_node_id)
            
    # 6. Add reserved Agentic RAG nodes from session cache for Milestone 10
    observations = session_data.get("observations", [])
    for idx, obs in enumerate(observations):
        obs_id = obs.get("id", f"obs_{idx+1}")
        if obs_id not in existing_ids:
            nodes.append({
                "id": obs_id,
                "label": obs.get("label", f"Observation {idx+1}"),
                "type": "observation_node",
                "content": obs.get("content", "")
            })
            existing_ids.add(obs_id)

    reflections = session_data.get("reflections", [])
    for idx, refl in enumerate(reflections):
        refl_id = refl.get("id", f"refl_{idx+1}")
        if refl_id not in existing_ids:
            nodes.append({
                "id": refl_id,
                "label": refl.get("label", f"Reflection {idx+1}"),
                "type": "reflection_node",
                "content": refl.get("content", "")
            })
            existing_ids.add(refl_id)

    tasks = session_data.get("tasks", [])
    for idx, tsk in enumerate(tasks):
        tsk_id = tsk.get("id", f"tsk_{idx+1}")
        if tsk_id not in existing_ids:
            nodes.append({
                "id": tsk_id,
                "label": tsk.get("label", f"Task {idx+1}"),
                "type": "task_node",
                "content": tsk.get("content", "")
            })
            existing_ids.add(tsk_id)

    plans = session_data.get("plans", [])
    for idx, pln in enumerate(plans):
        pln_id = pln.get("id", f"pln_{idx+1}")
        if pln_id not in existing_ids:
            nodes.append({
                "id": pln_id,
                "label": pln.get("label", f"Plan {idx+1}"),
                "type": "plan_node",
                "content": pln.get("content", "")
            })
            existing_ids.add(pln_id)

    tools = session_data.get("tools", [])
    for idx, tl in enumerate(tools):
        tl_id = tl.get("id", f"tl_{idx+1}")
        if tl_id not in existing_ids:
            nodes.append({
                "id": tl_id,
                "label": tl.get("label", f"Tool {idx+1}"),
                "type": "tool_node",
                "content": tl.get("content", "")
            })
            existing_ids.add(tl_id)
            
    return {
        "nodes": nodes,
        "edges": edges
    }
