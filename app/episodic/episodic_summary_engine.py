import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.episodic.episodic_models import ChainSummaryNode, EpisodeNode, TemporalChainNode
from app.episodic.episodic_store import get_episodes, get_experiences, append_chain_summary, append_chain
from app.retrieval.entity_extractor import extract_entities_from_text
from app.llm.ollama_client import ollama_client

def generate_chain_fallback_summary(episodes: List[EpisodeNode], experiences_dict: Dict[str, Any]) -> str:
    """
    Structured template fallback if Ollama fails.
    """
    entities = set()
    tools = set()
    successes = 0
    failures = 0
    
    for ep in episodes:
        entities.update(ep.entities)
        exp = experiences_dict.get(ep.episode_id)
        if exp:
            tools.update(exp.get("tools_used", []))
            if exp.get("success_status", True):
                successes += 1
            else:
                failures += 1
                
    summary = (
        f"Entities: {', '.join(list(entities)[:5]) if entities else 'None'}\n"
        f"Tools: {', '.join(list(tools)[:5]) if tools else 'None'}\n"
        f"Outcome: Compressed {len(episodes)} episodes\n"
        f"Failures: {failures}\n"
        f"Successes: {successes}"
    )
    return summary

def compress_temporal_chain_if_needed(chain: TemporalChainNode):
    """
    Refinement 19: If chain length is > 20, compress older episodes into a ChainSummaryNode
    and update the chain to only contain the remaining active episodes.
    """
    if len(chain.episode_ids) <= 20:
        return
        
    print(f"[SUMMARY ENGINE] Compressing temporal chain {chain.chain_id} because length {len(chain.episode_ids)} exceeds threshold 20.")
    
    # Compress the oldest 15 episodes
    compress_count = 15
    old_ep_ids = chain.episode_ids[:compress_count]
    remaining_ep_ids = chain.episode_ids[compress_count:]
    
    # Load episode nodes
    all_eps = {ep.episode_id: ep for ep in get_episodes()}
    old_episodes = [all_eps[eid] for eid in old_ep_ids if eid in all_eps]
    
    if not old_episodes:
        return
        
    # Load experience nodes
    experiences = get_experiences()
    exp_dict = {exp.episode_id: exp.model_dump() for exp in experiences}
    
    # Generate summary text
    entities_set = set()
    tools_set = set()
    success_count = 0
    failure_count = 0
    milestones = []
    
    for ep in old_episodes:
        entities_set.update(ep.entities)
        exp = exp_dict.get(ep.episode_id, {})
        tools_set.update(exp.get("tools_used", []))
        if exp.get("success_status", True):
            success_count += 1
        else:
            failure_count += 1
        milestones.append(f"Turn query: '{ep.query[:30]}...'")
        
    summary_text = ""
    try:
        # Construct summary using Ollama
        episodes_context = "\n".join([f"- Query: {ep.query} | Answer Summary: {ep.summary}" for ep in old_episodes])
        prompt = f"""You are a system compression engine. Summarize the following execution episodes in a single concise paragraph.
Include the major entities, successes, failures, and milestones.
Avoid any thinking process, chain of thought, or meta-commentary.

Episodes:
{episodes_context}
"""
        summary_text = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
        summary_text = summary_text.strip()
        if not summary_text or "error" in summary_text.lower():
            raise RuntimeError("Ollama failure during chain compression")
    except Exception:
        summary_text = generate_chain_fallback_summary(old_episodes, exp_dict)
        
    chain_summary_id = f"csm_{uuid.uuid4().hex[:8]}"
    summary_node = ChainSummaryNode(
        chain_summary_id=chain_summary_id,
        chain_id=chain.chain_id,
        summary_text=summary_text,
        major_entities=sorted(list(entities_set))[:5],
        successes=success_count,
        failures=failure_count,
        milestones=milestones[:5],
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Save the summary node
    append_chain_summary(summary_node)
    
    # Update the chain to drop compressed episodes
    chain.episode_ids = remaining_ep_ids
    chain.chain_summary = summary_text
    chain.updated_at = datetime.utcnow().isoformat()
    append_chain(chain)
    
    print(f"[SUMMARY ENGINE] Chain {chain.chain_id} compressed successfully. Created summary: {chain_summary_id}.")
