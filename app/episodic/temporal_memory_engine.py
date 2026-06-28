import uuid
from datetime import datetime
from typing import Optional, List
from app.episodic.episodic_models import TemporalChainNode, EpisodeNode
from app.episodic.episodic_store import get_chains, append_chain, get_episodes

def update_temporal_chains(new_episode: EpisodeNode) -> TemporalChainNode:
    """
    Appends the new episode to the active temporal chain if the time gap is < 10 minutes,
    otherwise spawns a new temporal chain.
    """
    all_chains = get_chains()
    now_str = datetime.utcnow().isoformat()
    
    active_chain: Optional[TemporalChainNode] = None
    if all_chains:
        # Get latest chain based on updated_at
        all_chains.sort(key=lambda c: c.updated_at, reverse=True)
        active_chain = all_chains[0]
        
    # Check time gap (10 minutes = 600 seconds)
    gap_threshold = 600.0
    gap_satisfied = False
    
    if active_chain and active_chain.episode_ids:
        # Load the last episode of the chain
        episodes_dict = {ep.episode_id: ep for ep in get_episodes()}
        last_ep_id = active_chain.episode_ids[-1]
        last_ep = episodes_dict.get(last_ep_id)
        
        if last_ep:
            t_last = datetime.fromisoformat(last_ep.timestamp)
            t_new = datetime.fromisoformat(new_episode.timestamp)
            gap = (t_new - t_last).total_seconds()
            if abs(gap) < gap_threshold:
                gap_satisfied = True
                
    if active_chain and gap_satisfied:
        # Append to active chain
        active_chain.episode_ids.append(new_episode.episode_id)
        active_chain.updated_at = new_episode.timestamp
        # Re-calculate chain importance (average of episode importances)
        episodes_list = get_episodes()
        ep_importances = [ep.importance_score for ep in episodes_list if ep.episode_id in active_chain.episode_ids]
        if ep_importances:
            active_chain.chain_importance = sum(ep_importances) / len(ep_importances)
            
        append_chain(active_chain)
        print(f"[TEMPORAL ENGINE] Appended episode {new_episode.episode_id} to active chain {active_chain.chain_id}.")
        return active_chain
    else:
        # Spawn new chain
        chain_id = f"ch_{uuid.uuid4().hex[:8]}"
        new_chain = TemporalChainNode(
            chain_id=chain_id,
            episode_ids=[new_episode.episode_id],
            chain_summary=None,
            chain_importance=new_episode.importance_score,
            created_at=new_episode.timestamp,
            updated_at=new_episode.timestamp
        )
        append_chain(new_chain)
        print(f"[TEMPORAL ENGINE] Spawned new chain {chain_id} with episode {new_episode.episode_id}.")
        return new_chain
