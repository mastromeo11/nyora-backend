from datetime import datetime
from typing import List, Dict, Any, Set, Tuple
from app.episodic.episodic_models import EpisodeNode
from app.episodic.episodic_store import (
    get_episodes, get_chains, get_clusters, get_replays, get_chain_summaries
)
from app.embedding.text_embedder import embed_text
from app.config import (
    TEMPORAL_WEIGHT, IMPORTANCE_WEIGHT, RECENCY_WEIGHT, SIMILARITY_WEIGHT,
    MAX_EPISODE_DEPTH, MAX_EXPERIENCE_CHAIN, MAX_TOTAL_EPISODES_VISITED
)

def retrieve_episodic_context(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Step 12: Performs hybrid retrieval using BGE similarity, importance, recency, and temporal context.
    Enforces loop protection recursively.
    """
    episodes = get_episodes()
    chains = get_chains()
    clusters = get_clusters()
    replays = get_replays()
    summaries = get_chain_summaries()
    
    if not episodes:
        return {
            "episodes": [],
            "replays": [],
            "chains": [],
            "clusters": [],
            "summaries": []
        }
        
    query_emb = embed_text([query])[0]
    
    # Visited sets to avoid replay recursion (Refinement 9)
    visited_episode_ids: Set[str] = set()
    visited_chain_ids: Set[str] = set()
    
    scored_candidates = []
    
    # Index chains for fast lookup
    chain_by_episode = {}
    for ch in chains:
        for ep_id in ch.episode_ids:
            chain_by_episode[ep_id] = ch
            
    # Limit number of evaluated nodes to avoid performance degradation
    eval_candidates = episodes[:MAX_TOTAL_EPISODES_VISITED]
    
    for ep in eval_candidates:
        if len(visited_episode_ids) >= MAX_TOTAL_EPISODES_VISITED:
            break
            
        ep_id = ep.episode_id
        if ep_id in visited_episode_ids:
            continue
        visited_episode_ids.add(ep_id)
        
        # 1. Similarity
        emb = ep.query_embedding
        if not emb:
            emb = embed_text([ep.query])[0]
            ep.query_embedding = emb
        similarity = sum(a * b for a, b in zip(query_emb, emb))
        
        # 2. Importance
        importance = ep.importance_score
        
        # 3. Recency
        time_diff = (datetime.utcnow() - datetime.fromisoformat(ep.timestamp)).total_seconds()
        recency = 1.0 / (1.0 + time_diff / 86400.0)
        
        # 4. Temporal context similarity of neighboring episodes in chain
        temporal_context = 0.0
        ch = chain_by_episode.get(ep_id)
        if ch and ch.chain_id not in visited_chain_ids:
            visited_chain_ids.add(ch.chain_id)
            
            # Fetch neighbors in chain (up to MAX_EPISODE_DEPTH)
            ep_ids = ch.episode_ids
            if ep_id in ep_ids:
                idx = ep_ids.index(ep_id)
                start = max(0, idx - MAX_EPISODE_DEPTH)
                end = min(len(ep_ids), idx + 1 + MAX_EPISODE_DEPTH)
                
                neighbor_ids = [eid for idx_n, eid in enumerate(ep_ids[start:end]) if eid != ep_id]
                
                neighbor_sims = []
                ep_dict = {e.episode_id: e for e in episodes}
                
                for n_id in neighbor_ids[:MAX_EXPERIENCE_CHAIN]:
                    n_ep = ep_dict.get(n_id)
                    if n_ep:
                        n_emb = n_ep.query_embedding
                        if not n_emb:
                            n_emb = embed_text([n_ep.query])[0]
                            n_ep.query_embedding = n_emb
                        n_sim = sum(a * b for a, b in zip(query_emb, n_emb))
                        neighbor_sims.append(n_sim)
                        
                if neighbor_sims:
                    temporal_context = sum(neighbor_sims) / len(neighbor_sims)
                    
        # Total Hybrid Score
        score = (SIMILARITY_WEIGHT * similarity +
                 IMPORTANCE_WEIGHT * importance +
                 RECENCY_WEIGHT * recency +
                 TEMPORAL_WEIGHT * temporal_context)
                 
        scored_candidates.append((score, ep))
        
    # Sort by score descending
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = [item[1] for item in scored_candidates[:limit]]
    
    # 5. Extract associated models
    top_ep_ids = {ep.episode_id for ep in top_candidates}
    
    matched_replays = [r for r in replays if r.source_episode in top_ep_ids or r.target_episode in top_ep_ids]
    matched_chains = [ch for ch in chains if any(eid in top_ep_ids for eid in ch.episode_ids)]
    matched_clusters = [cl for cl in clusters if any(eid in top_ep_ids for eid in cl.episodes)]
    matched_chain_ids = {ch.chain_id for ch in matched_chains}
    matched_summaries = [s for s in summaries if s.chain_id in matched_chain_ids]
    
    # Limit collections to prevent prompt bloat
    return {
        "episodes": top_candidates,
        "replays": matched_replays[:5],
        "chains": matched_chains[:3],
        "clusters": matched_clusters[:3],
        "summaries": matched_summaries[:3]
    }
