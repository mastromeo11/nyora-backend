from app.episodic.episodic_store import load_episodic_store, save_episodic_store
from app.config import MEMORY_DECAY_FACTOR, IMPORTANCE_DECAY_FACTOR

def decay_episodic_memory():
    """
    Decays the importance score and confidence value of all episodes stored in the database.
    """
    mem = load_episodic_store()
    episodes = mem.get("episodes", {})
    
    for ep_data in episodes.values():
        if "importance_score" in ep_data:
            ep_data["importance_score"] = max(0.0, float(ep_data["importance_score"]) * MEMORY_DECAY_FACTOR)
        if "confidence" in ep_data:
            ep_data["confidence"] = max(0.0, float(ep_data["confidence"]) * IMPORTANCE_DECAY_FACTOR)
            
    save_episodic_store()
    print("[DECAY ENGINE] Executed decay cycle on episodic database.")
