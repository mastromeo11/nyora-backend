import os
import json
from app.retrieval.session_memory import get_session, _get_session_path

def compress_older_turns(session_id: str):
    """
    Prevents context size explosion by truncating the session history turns list
    to keep only the last 10 turns. Summarization logic is handled separately in
    conversation_summarizer.py.
    """
    turns = get_session(session_id)
    if len(turns) <= 10:
        return
        
    turns_to_keep = turns[-10:]
    
    # Save the truncated turns list back to session file
    path = _get_session_path(session_id)
    try:
        temp_path = path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump([t.dict() for t in turns_to_keep], f, indent=2)
        os.replace(temp_path, path)
        print(f"[COMPRESSOR] Truncated turns for session {session_id} to last 10 turns.")
    except Exception as e:
        print(f"[COMPRESSOR] Error saving compressed turns to {session_id}: {e}")
