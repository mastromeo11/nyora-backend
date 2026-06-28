import uuid
from datetime import datetime
from typing import List, Optional
from app.episodic.episodic_models import MemoryClusterNode, EpisodeNode
from app.episodic.episodic_store import get_clusters, append_cluster, get_episodes, get_experiences
from app.embedding.text_embedder import embed_text

def cluster_episode(new_episode: EpisodeNode):
    """
    Assigns the new episode to an existing semantic cluster if similarity >= 0.85,
    otherwise spawns a new cluster node.
    """
    clusters = get_clusters()
    now_str = datetime.utcnow().isoformat()
    
    # 1. Obtain query embedding
    emb = new_episode.query_embedding
    if not emb:
        emb = embed_text([new_episode.query])[0]
        new_episode.query_embedding = emb
        
    matched_cluster: Optional[MemoryClusterNode] = None
    highest_sim = 0.0
    similarity_threshold = 0.85
    
    for c in clusters:
        c_emb = c.cluster_center_embedding
        if not c_emb:
            c_emb = embed_text([c.cluster_center_query])[0]
            c.cluster_center_embedding = c_emb
            
        sim = sum(a * b for a, b in zip(emb, c_emb))
        if sim > highest_sim:
            highest_sim = sim
            matched_cluster = c
            
    if matched_cluster and highest_sim >= similarity_threshold:
        # Append episode to existing cluster
        if new_episode.episode_id not in matched_cluster.episodes:
            matched_cluster.episodes.append(new_episode.episode_id)
        matched_cluster.frequency = len(matched_cluster.episodes)
        matched_cluster.last_updated = now_str
        
        # Recalculate success rate and importance
        recalculate_cluster_stats(matched_cluster)
        append_cluster(matched_cluster)
        new_episode.cluster_id = matched_cluster.cluster_id
        print(f"[CLUSTER ENGINE] Assigned episode {new_episode.episode_id} to cluster {matched_cluster.cluster_id} (similarity: {highest_sim:.4f}).")
    else:
        # Spawn new cluster
        cluster_id = f"cl_{uuid.uuid4().hex[:8]}"
        new_cluster = MemoryClusterNode(
            cluster_id=cluster_id,
            episodes=[new_episode.episode_id],
            cluster_center_query=new_episode.query,
            cluster_center_embedding=emb,
            frequency=1,
            importance_score=new_episode.importance_score,
            success_rate=1.0, # Will be updated in stats recalculation
            last_updated=now_str
        )
        recalculate_cluster_stats(new_cluster)
        append_cluster(new_cluster)
        new_episode.cluster_id = cluster_id
        print(f"[CLUSTER ENGINE] Created new cluster {cluster_id} centered at: '{new_episode.query[:30]}...'.")

def recalculate_cluster_stats(cluster: MemoryClusterNode):
    """
    Computes cluster metrics:
    cluster_importance = 0.4 * frequency_score + 0.3 * success_rate + 0.3 * recency
    """
    all_eps = {ep.episode_id: ep for ep in get_episodes()}
    all_exps = {exp.episode_id: exp for exp in get_experiences()}
    
    eps_in_cluster = [all_eps[eid] for eid in cluster.episodes if eid in all_eps]
    
    if not eps_in_cluster:
        return
        
    # 1. Success rate
    successes = 0
    total = 0
    for ep in eps_in_cluster:
        exp = all_exps.get(ep.episode_id)
        if exp:
            total += 1
            if exp.success_status:
                successes += 1
    cluster.success_rate = (successes / total) if total > 0 else 1.0
    
    # 2. Frequency score (scaled log/linear, e.g. min(count / 10.0, 1.0))
    freq_score = min(len(eps_in_cluster) / 10.0, 1.0)
    
    # 3. Recency of the latest episode
    latest_timestamp = max(ep.timestamp for ep in eps_in_cluster)
    time_diff = (datetime.utcnow() - datetime.fromisoformat(latest_timestamp)).total_seconds()
    recency = 1.0 / (1.0 + time_diff / 86400.0)
    
    # 4. Importance score
    cluster.importance_score = (0.4 * freq_score) + (0.3 * cluster.success_rate) + (0.3 * recency)
