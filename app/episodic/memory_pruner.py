from app.episodic.episodic_store import load_episodic_store, save_episodic_store
from app.config import MIN_EPISODE_IMPORTANCE

def prune_episodic_memory():
    """
    Cleans up the database by removing zero-weight, isolated, or obsolete records.
    Returns the count of pruned items.
    """
    mem = load_episodic_store()
    episodes = mem.setdefault("episodes", {})
    experiences = mem.setdefault("experiences", {})
    replays = mem.setdefault("replays", {})
    chains = mem.setdefault("temporal_chains", {})
    clusters = mem.setdefault("clusters", {})
    failure_replays = mem.setdefault("failure_replays", {})
    chain_summaries = mem.setdefault("chain_summaries", {})
    
    pruned_count = 0
    
    # 1. Identify low-value (zero-weight) episodes to delete
    to_delete_episodes = set()
    for ep_id, ep_data in list(episodes.items()):
        importance = ep_data.get("importance_score", 1.0)
        if importance < MIN_EPISODE_IMPORTANCE:
            to_delete_episodes.add(ep_id)
            
    # 2. Identify referenced episode IDs in active groupings to prevent deleting connected nodes
    referenced_in_chains = set()
    for chain_data in chains.values():
        referenced_in_chains.update(chain_data.get("episode_ids", []))
        
    referenced_in_clusters = set()
    for cluster_data in clusters.values():
        referenced_in_clusters.update(cluster_data.get("episodes", []))
        
    referenced_in_replays = set()
    for rep_data in replays.values():
        referenced_in_replays.add(rep_data.get("source_episode"))
        referenced_in_replays.add(rep_data.get("target_episode"))
        
    # Isolated check: no references in chains, clusters, replays, and no experiences
    for ep_id in list(episodes.keys()):
        if ep_id not in referenced_in_chains and ep_id not in referenced_in_clusters and ep_id not in referenced_in_replays:
            # Check if there is an associated experience
            has_exp = any(exp.get("episode_id") == ep_id for exp in experiences.values())
            if not has_exp:
                to_delete_episodes.add(ep_id)
                
    # 3. Perform deletes on episodes and their direct sub-experiences
    for ep_id in to_delete_episodes:
        episodes.pop(ep_id, None)
        pruned_count += 1
        
        # Clean up experiences
        for exp_id in list(experiences.keys()):
            if experiences[exp_id].get("episode_id") == ep_id:
                experiences.pop(exp_id, None)
                
    # 4. Clean up broken replay links
    for rep_id, rep_data in list(replays.items()):
        src = rep_data.get("source_episode")
        tgt = rep_data.get("target_episode")
        if src not in episodes or tgt not in episodes:
            replays.pop(rep_id, None)
            pruned_count += 1
            
    # 5. Clean up broken/empty temporal chains
    for chain_id, chain_data in list(chains.items()):
        eps = [eid for eid in chain_data.get("episode_ids", []) if eid in episodes]
        importance = chain_data.get("chain_importance", 1.0)
        
        if not eps or importance < MIN_EPISODE_IMPORTANCE:
            chains.pop(chain_id, None)
            pruned_count += 1
            # Also clean up linked summaries
            for cs_id, cs_data in list(chain_summaries.items()):
                if cs_data.get("chain_id") == chain_id:
                    chain_summaries.pop(cs_id, None)
        else:
            chain_data["episode_ids"] = eps
            
    # 6. Clean up broken/expired clusters
    for cluster_id, cluster_data in list(clusters.items()):
        eps = [eid for eid in cluster_data.get("episodes", []) if eid in episodes]
        if not eps or cluster_data.get("importance_score", 1.0) < MIN_EPISODE_IMPORTANCE:
            clusters.pop(cluster_id, None)
            pruned_count += 1
        else:
            cluster_data["episodes"] = eps
            cluster_data["frequency"] = len(eps)
            
    # 7. Clean up broken/empty failure replays
    for fail_id, fail_data in list(failure_replays.items()):
        if fail_data.get("frequency", 0) <= 0:
            failure_replays.pop(fail_id, None)
            pruned_count += 1
            
    save_episodic_store()
    print(f"[PRUNER] Pruned {pruned_count} items from the episodic database.")
    return pruned_count
