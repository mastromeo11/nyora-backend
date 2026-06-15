from typing import List, Dict, Any
from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.config import MAX_OBSERVATION_MEMORY

# Track hits in metrics
_obs_mem_hits = 0
_obs_mem_queries = 0

def increment_obs_mem_query():
    global _obs_mem_queries
    _obs_mem_queries += 1

def increment_obs_mem_hit():
    global _obs_mem_hits
    _obs_mem_hits += 1

def get_obs_mem_hit_rate() -> float:
    global _obs_mem_hits, _obs_mem_queries
    if _obs_mem_queries > 0:
        return round(_obs_mem_hits / _obs_mem_queries, 4)
    return 0.0

def store_observations(session_id: str, new_observations: List[Any]):
    """
    Stores observations in the session cache with timestamp and a decay turns tracker.
    """
    cache = get_session_cache(session_id)
    obs_mem = cache.setdefault("observation_memory", [])
    
    # 1. Decay existing observations (multiply score by 0.95)
    for obs in obs_mem:
        obs["turns_since_stored"] = obs.get("turns_since_stored", 0) + 1
        obs["score"] = obs.get("score", 1.0) * 0.95
        
    # 2. Add new observations
    for obs in new_observations:
        obs_dict = {
            "observation_id": obs.observation_id,
            "tool_name": obs.tool_name,
            "content": obs.content,
            "timestamp": obs.timestamp,
            "score": 1.0,
            "turns_since_stored": 0
        }
        obs_mem.append(obs_dict)
        
    # 3. Filter out highly decayed observations (score < 0.25)
    obs_mem = [obs for obs in obs_mem if obs["score"] >= 0.25]
    
    # 4. Prune to MAX_OBSERVATION_MEMORY
    if len(obs_mem) > MAX_OBSERVATION_MEMORY:
        obs_mem = sorted(obs_mem, key=lambda x: x["score"], reverse=True)[:MAX_OBSERVATION_MEMORY]
        
    cache["observation_memory"] = obs_mem
    save_session_cache(session_id, cache)
    print(f"[OBS MEMORY] Stored {len(new_observations)} observations. Active size: {len(obs_mem)}")

def retrieve_cached_observations(session_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Retrieves observations relevant to the query keywords from observation memory.
    """
    increment_obs_mem_query()
    cache = get_session_cache(session_id)
    obs_mem = cache.get("observation_memory", [])
    
    q_words = set(query.lower().split())
    relevant = []
    
    for obs in obs_mem:
        content_lower = obs["content"].lower()
        # Simple overlap relevance check
        if any(w in content_lower for w in q_words if len(w) > 3):
            relevant.append(obs)
            
    if relevant:
        increment_obs_mem_hit()
        print(f"[OBS MEMORY] Retrieved {len(relevant)} cached observations matching query.")
        
    return relevant
