from typing import List, Dict, Any
from app.episodic.episodic_store import get_episodes

def compile_episodic_explanation(replays: List[Any]) -> str:
    """
    Step 16: Generates a natural explanation indicating how prior replayed experiences aided retrieval.
    """
    if not replays:
        return ""
        
    episodes = get_episodes()
    ep_dict = {ep.episode_id: ep for ep in episodes}
    
    entities_seen = set()
    success_count = 0
    
    for r in replays:
        # Pydantic or dict check
        src_id = r.source_episode if hasattr(r, "source_episode") else r.get("source_episode")
        src_ep = ep_dict.get(src_id)
        if src_ep:
            entities_seen.update(src_ep.entities)
            success_count += 1
            
    if success_count > 0:
        ents_list = list(entities_seen)
        if ents_list:
            # Join up to 3 entities nicely
            ents_str = ", ".join(ents_list[:2])
            if len(ents_list) > 2:
                ents_str += f" and {ents_list[2]}"
        else:
            ents_str = "system components"
            
        return f"Similar previous experiences involving {ents_str} were successfully replayed, improving retrieval quality."
        
    return ""
