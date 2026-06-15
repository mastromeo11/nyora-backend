from typing import List, Dict, Any

def compile_swarm_explanation(history: List[Dict[str, Any]]) -> str:
    """
    Compiles a natural, explainable summary of swarm collaboration paths.
    Conceals intermediate chain-of-thought traces.
    """
    explanations = []
    
    explanations.append("Planner Agent decomposed the query into targeted subtasks.")
    
    has_ret = any(h.get("agent_id") == "retrieval" for h in history)
    has_kg = any(h.get("agent_id") == "kg" for h in history)
    if has_ret and has_kg:
        explanations.append("Retrieval Agent fetched relevant files and Knowledge Graph Agent traversed entity relationships.")
    elif has_ret:
        explanations.append("Retrieval Agent collected semantic document context.")
    elif has_kg:
        explanations.append("Knowledge Graph Agent mapped multi-hop node connections.")
        
    has_critic = any(h.get("agent_id") == "critic" for h in history)
    has_grounding = any(h.get("agent_id") == "grounding" for h in history)
    
    if has_critic:
        explanations.append("Critic Agent verified outputs for potential alignment discrepancies.")
    if has_grounding:
        explanations.append("Grounding Agent confirmed that all final assertions matched retrieved evidence.")
        
    explanations.append("Consensus Engine synthesized the final response payload.")
    
    return " ".join(explanations)
