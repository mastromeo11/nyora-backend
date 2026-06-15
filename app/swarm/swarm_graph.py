from typing import List, Dict, Any
from app.config import MAX_AGENT_DEPTH, MAX_MESSAGE_CHAIN

def extend_swarm_graph(
    base_graph: Dict[str, Any],
    agents: List[Dict[str, Any]],
    messages: List[Dict[str, Any]],
    delegations: List[Dict[str, Any]],
    collaborations: List[Dict[str, Any]],
    consensus_nodes: List[Dict[str, Any]],
    shared_memories: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extends the unified graph with swarm collaboration entities and edges.
    Applies loop and depth checking bounds.
    """
    nodes = base_graph.get("nodes", [])
    edges = base_graph.get("edges", [])
    
    existing_ids = {n["id"] for n in nodes}
    
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
            
    def add_edge(source: str, target: str, edge_type: str, **kwargs):
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

    # 1. Add AgentNodes (up to depth limit)
    for agent in agents[:MAX_AGENT_DEPTH]:
        a_id = agent.get("agent_id", "")
        if a_id:
            add_node(a_id, f"Agent: {agent.get('agent_name')}", "agent_node", role=agent.get("role"))
        
    # 2. Add Messages (up to chain limit)
    for msg in messages[:MAX_MESSAGE_CHAIN]:
        m_id = msg.get("message_id", "")
        if m_id:
            add_node(m_id, f"Msg: {msg.get('content')[:15]}...", "message_node")
            
            # Link MessageNode -> AgentNode (receiver)
            if msg.get("receiver"):
                add_edge(m_id, msg.get("receiver"), "message_to_agent")
            # Link AgentNode (sender) -> MessageNode
            if msg.get("sender"):
                add_edge(msg.get("sender"), m_id, "agent_to_message")
        
    # 3. Add Delegations
    for dg in delegations[:MAX_MESSAGE_CHAIN]:
        dg_id = dg.get("delegation_id", f"dg_{dg.get('sender')}_{dg.get('receiver')}")
        add_node(dg_id, f"Delegation: {dg.get('task')[:15]}...", "delegation_node")
        
        if dg.get("sender"):
            add_edge(dg.get("sender"), dg_id, "agent_delegation")
        if dg.get("receiver"):
            add_edge(dg_id, dg.get("receiver"), "delegation_target")
        
    # 4. Add Collaborations
    for col in collaborations[:MAX_MESSAGE_CHAIN]:
        c_id = col.get("collaboration_id", "")
        if c_id:
            add_node(c_id, f"Collaboration Context: {col.get('context')[:15]}...", "collaboration_node")
            for participant in col.get("participants", []):
                add_edge(participant, c_id, "agent_collaboration")
            
    # 5. Add Consensus Nodes
    for con in consensus_nodes[:MAX_MESSAGE_CHAIN]:
        con_id = con.get("consensus_id", "")
        if con_id:
            add_node(con_id, f"Consensus: {con.get('agreed_fact')[:15]}...", "consensus_node", score=con.get("consensus_score"))
            add_edge("grounding", con_id, "grounding_to_consensus")
            add_edge(con_id, "planner", "consensus_feedback")
        
    # 6. Add Shared Memory nodes
    for sm in shared_memories[:MAX_MESSAGE_CHAIN]:
        sm_key = sm.get("key", "")
        sm_id = f"sm_{sm_key}"
        add_node(sm_id, f"SharedMem: {sm_key}", "shared_memory_node", version=sm.get("version"))
        
        for col in collaborations[:MAX_MESSAGE_CHAIN]:
            if col.get("collaboration_id"):
                add_edge(col.get("collaboration_id"), sm_id, "collaboration_to_shared_memory")
            
    add_edge("critic", "planner", "critic_to_planner")
    
    return {
        "nodes": nodes,
        "edges": edges
    }
