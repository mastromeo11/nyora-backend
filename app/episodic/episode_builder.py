import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from app.episodic.episodic_models import EpisodeNode, ExperienceNode
from app.episodic.episodic_store import append_episode, append_experience, get_episodes
from app.episodic.query_signature_engine import generate_query_signature
from app.retrieval.entity_extractor import extract_entities_from_text
from app.embedding.text_embedder import embed_text
from app.config import ENABLE_IMPORTANCE_SCORING, ENABLE_MEMORY_SUMMARIZATION

def generate_fallback_summary(
    query: str, 
    answer: str, 
    entities: List[str], 
    tools_used: List[str], 
    success: bool, 
    failure_reason: Optional[str] = None
) -> str:
    outcome = "Success" if success else "Failure"
    failures = failure_reason if failure_reason else ("None" if success else "Execution failure")
    successes = "Task solved successfully" if success else "None"
    
    summary = (
        f"Entities: {', '.join(entities) if entities else 'None'}\n"
        f"Tools: {', '.join(tools_used) if tools_used else 'None'}\n"
        f"Outcome: {outcome}\n"
        f"Failures: {failures}\n"
        f"Successes: {successes}"
    )
    return summary

def generate_episode_summary(
    query: str, 
    answer: str, 
    entities: List[str], 
    tools_used: List[str], 
    success: bool, 
    failure_reason: Optional[str] = None
) -> str:
    if not ENABLE_MEMORY_SUMMARIZATION:
        return generate_fallback_summary(query, answer, entities, tools_used, success, failure_reason)
        
    try:
        from app.llm.ollama_client import ollama_client
        prompt = f"""Summarize the following query and answer interaction in a single, short sentence focusing on the technical actions and outcomes.
Query: {query}
Answer: {answer}
Summary:"""
        # Call Ollama
        summary = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
        summary = summary.strip().replace("Summary:", "").strip()
        if not summary or "error" in summary.lower() or "ollama" in summary.lower():
            raise RuntimeError("Ollama failure")
        return summary
    except Exception:
        return generate_fallback_summary(query, answer, entities, tools_used, success, failure_reason)

def build_and_store_episode(
    query: str,
    answer: str,
    confidence_label_or_score: Union[str, float] = 1.0,
    grounding_report: Optional[List[Dict[str, Any]]] = None,
    user_signal: float = 1.0,
    experience_type: str = "general",
    supporting_evidence_ids: Optional[List[str]] = None,
    planner_trace_ids: Optional[List[str]] = None,
    critic_trace_ids: Optional[List[str]] = None,
    consensus_trace_ids: Optional[List[str]] = None,
    agent_ids: Optional[List[str]] = None,
    tools_used: Optional[List[str]] = None,
    observation_ids: Optional[List[str]] = None,
    reflection_ids: Optional[List[str]] = None,
    consensus_ids: Optional[List[str]] = None,
    success_status: bool = True,
    execution_latency: float = 0.0,
    failure_reason: Optional[str] = None
) -> tuple:
    """
    Builds and saves an EpisodeNode and its linked ExperienceNode.
    Enforces signature deduplication and embedding pre-generation.
    """
    # 1. Default lists
    supporting_evidence_ids = supporting_evidence_ids or []
    planner_trace_ids = planner_trace_ids or []
    critic_trace_ids = critic_trace_ids or []
    consensus_trace_ids = consensus_trace_ids or []
    agent_ids = agent_ids or []
    tools_used = tools_used or []
    observation_ids = observation_ids or []
    reflection_ids = reflection_ids or []
    consensus_ids = consensus_ids or []
    
    # 2. Extract entities
    entities = list(extract_entities_from_text(query + " " + answer))
    
    # 3. Signature deduplication (Prevent duplicate episodes)
    sig = generate_query_signature(query, entities, experience_type)
    
    # Check if signature matches an existing episode
    existing_eps = get_episodes()
    for ep in existing_eps:
        # Check if hash of existing ep matches signature
        existing_sig = generate_query_signature(ep.query, ep.entities, ep.experience_type)
        if existing_sig == sig:
            print(f"[EPISODE BUILDER] Duplicate query signature detected: {sig}. Skipping creation.")
            # Retrieve corresponding experience if needed
            return ep, None
            
    # 4. Map confidence
    confidence_val = 1.0
    if isinstance(confidence_label_or_score, str):
        lbl = confidence_label_or_score.lower()
        if "high" in lbl:
            confidence_val = 1.0
        elif "med" in lbl:
            confidence_val = 0.6
        else:
            confidence_val = 0.3
    else:
        confidence_val = float(confidence_label_or_score)
        
    # 5. Compute grounding score
    grounding_score = 1.0
    if grounding_report:
        total = len(grounding_report)
        supported = sum(1 for item in grounding_report if str(item.get("status", "")).lower() in ("supported", "bypassed for meta-query", "valid"))
        if total > 0:
            grounding_score = supported / total
            
    # 6. Compute importance score
    importance_score = 0.0
    if ENABLE_IMPORTANCE_SCORING:
        importance_score = (0.30 * confidence_val) + (0.25 * grounding_score) + (0.25 * user_signal) + (0.20 * 1.0)
        
    # 7. Generate turn summary
    summary = generate_episode_summary(query, answer, entities, tools_used, success_status, failure_reason)
    
    # 8. Embed query and summary
    query_emb = embed_text([query])[0]
    summary_emb = embed_text([summary])[0]
    
    # 9. Create Episode Node
    episode_id = f"ep_{uuid.uuid4().hex[:8]}"
    now_str = datetime.utcnow().isoformat()
    
    ep_node = EpisodeNode(
        episode_id=episode_id,
        timestamp=now_str,
        query=query,
        answer=answer,
        entities=entities,
        agent_trace_ids=planner_trace_ids + critic_trace_ids + consensus_trace_ids,
        importance_score=importance_score,
        confidence=confidence_val,
        experience_type=experience_type,
        supporting_evidence_ids=supporting_evidence_ids,
        summary=summary,
        created_at=now_str,
        updated_at=now_str,
        last_accessed=now_str,
        query_embedding=query_emb,
        summary_embedding=summary_emb,
        access_count=1,
        planner_trace_ids=planner_trace_ids,
        critic_trace_ids=critic_trace_ids,
        consensus_trace_ids=consensus_trace_ids,
        agent_ids=agent_ids
    )
    
    # 10. Create Experience Node
    experience_id = f"exp_{uuid.uuid4().hex[:8]}"
    exp_node = ExperienceNode(
        experience_id=experience_id,
        episode_id=episode_id,
        tools_used=tools_used,
        agent_trace_ids=planner_trace_ids + critic_trace_ids + consensus_trace_ids,
        reflection_ids=reflection_ids,
        consensus_ids=consensus_ids,
        success_status=success_status,
        execution_latency=execution_latency,
        failure_reason=failure_reason,
        importance_score=importance_score,
        confidence=confidence_val,
        timestamp=now_str
    )
    
    # 11. Append nodes to store
    append_episode(ep_node)
    append_experience(exp_node)
    
    return ep_node, exp_node
