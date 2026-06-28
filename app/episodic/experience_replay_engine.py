import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.episodic.episodic_models import ReplayNode, EpisodeNode
from app.episodic.episodic_store import get_episodes, get_experiences, get_replays, append_replay
from app.embedding.text_embedder import embed_text
from app.config import TEMPORAL_WEIGHT, IMPORTANCE_WEIGHT, RECENCY_WEIGHT, SIMILARITY_WEIGHT

def record_replay(source_id: str, target_id: str, similarity: float, confidence: float):
    """
    Saves or updates a ReplayNode between source and target episodes.
    Enforces replay reinforcement instead of replacement.
    """
    replays = get_replays()
    now_str = datetime.utcnow().isoformat()
    
    # Check if a replay link already exists between these two episodes
    existing_rep = None
    for r in replays:
        if r.source_episode == source_id and r.target_episode == target_id:
            existing_rep = r
            break
            
    if existing_rep:
        existing_rep.frequency += 1
        existing_rep.success_count += 1
        existing_rep.last_seen = now_str
        existing_rep.score += confidence
        append_replay(existing_rep)
        print(f"[REPLAY ENGINE] Reinforced replay link: {existing_rep.replay_id} (frequency: {existing_rep.frequency}).")
    else:
        replay_id = f"rep_{uuid.uuid4().hex[:8]}"
        new_rep = ReplayNode(
            replay_id=replay_id,
            source_episode=source_id,
            target_episode=target_id,
            similarity_score=similarity,
            timestamp=now_str,
            frequency=1,
            success_count=1,
            last_seen=now_str,
            score=confidence
        )
        append_replay(new_rep)
        print(f"[REPLAY ENGINE] Created new replay link: {replay_id} (src: {source_id} -> tgt: {target_id}).")

def retrieve_replays_for_query(query: str, limit: int = 5) -> List[Tuple[float, EpisodeNode]]:
    """
    Retrieves and ranks prior experiences for replay context based on the hybrid formula:
    score = 0.30 * similarity + 0.25 * success_rate + 0.20 * importance + 0.15 * recency + 0.10 * confidence.
    Successful experiences always outrank failures.
    """
    episodes = get_episodes()
    experiences = get_experiences()
    
    if not episodes:
        return []
        
    query_emb = embed_text([query])[0]
    
    # Index experiences by episode_id
    exp_dict = {exp.episode_id: exp for exp in experiences}
    
    scored_candidates = []
    for ep in episodes:
        emb = ep.query_embedding
        if not emb:
            emb = embed_text([ep.query])[0]
            ep.query_embedding = emb
            
        similarity = sum(a * b for a, b in zip(query_emb, emb))
        
        # Experience stats
        exp = exp_dict.get(ep.episode_id)
        success_status = exp.success_status if exp else True
        success_rate = 1.0 if success_status else 0.0
        
        importance = ep.importance_score
        
        # Recency
        time_diff = (datetime.utcnow() - datetime.fromisoformat(ep.timestamp)).total_seconds()
        recency = 1.0 / (1.0 + time_diff / 86400.0)
        
        confidence = ep.confidence
        
        # Score calculation
        score = (0.30 * similarity) + (0.25 * success_rate) + (0.20 * importance) + (0.15 * recency) + (0.10 * confidence)
        
        scored_candidates.append((score, success_status, similarity, ep))
        
    # Successful experiences always outrank failures
    # So we sort by success_status DESC, then by score DESC
    scored_candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    
    # Return top ranked episodes with their final scores
    return [(item[0], item[3]) for item in scored_candidates[:limit]]
