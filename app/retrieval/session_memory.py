import os
import json
import time
from datetime import datetime
from typing import List
from app.retrieval.memory_models import ConversationTurn

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "storage/sessions"))

def _get_session_path(session_id: str) -> str:
    os.makedirs(SESSION_DIR, exist_ok=True)
    # Sanitize session_id to prevent path traversal
    safe_session_id = "".join([c for c in session_id if c.isalnum() or c in ("-", "_")])
    if not safe_session_id:
        safe_session_id = "default_session"
    return os.path.join(SESSION_DIR, f"session_{safe_session_id}.json")

def create_session(session_id: str):
    path = _get_session_path(session_id)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=2)

def get_session(session_id: str) -> List[ConversationTurn]:
    path = _get_session_path(session_id)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return [ConversationTurn(**turn) for turn in data]
    except Exception as e:
        print(f"Error loading session {session_id}: {e}")
        return []

def add_turn(session_id: str, turn: ConversationTurn):
    turns = get_session(session_id)
    turns.append(turn)
    path = _get_session_path(session_id)
    try:
        # Write to temp file and rename to avoid corruption
        temp_path = path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump([t.dict() for t in turns], f, indent=2)
        os.replace(temp_path, path)
    except Exception as e:
        print(f"Error saving turn to session {session_id}: {e}")

def get_recent_turns(session_id: str, count: int) -> List[ConversationTurn]:
    turns = get_session(session_id)
    return turns[-count:]

def clear_session(session_id: str):
    path = _get_session_path(session_id)
    if os.path.exists(path):
        try:
            with open(path, "w") as f:
                json.dump([], f, indent=2)
        except Exception as e:
            print(f"Error clearing session {session_id}: {e}")

def expire_old_sessions(timeout_minutes: int):
    """
    Deletes session files that haven't been modified in timeout_minutes.
    """
    if not os.path.exists(SESSION_DIR):
        return
    now = time.time()
    limit_seconds = timeout_minutes * 60
    for filename in os.listdir(SESSION_DIR):
        if filename.startswith("session_") and filename.endswith(".json"):
            path = os.path.join(SESSION_DIR, filename)
            try:
                mod_time = os.path.getmtime(path)
                if now - mod_time > limit_seconds:
                    os.remove(path)
                    print(f"Expired and deleted session file: {filename}")
            except Exception as e:
                print(f"Error processing expiration for {filename}: {e}")
