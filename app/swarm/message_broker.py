import uuid
import threading
from datetime import datetime
from typing import Dict, List, Any
from app.swarm.agent_store import append_message

_broker_lock = threading.Lock()
_messages_db: List[Dict[str, Any]] = []

def send_message(sender: str, receiver: str, content: str) -> Dict[str, Any]:
    now_str = datetime.utcnow().isoformat()
    msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    
    msg_data = {
        "message_id": msg_id,
        "sender": sender,
        "receiver": receiver,
        "content": content,
        "timestamp": now_str
    }
    
    with _broker_lock:
        _messages_db.append(msg_data)
        
    # Persist to agent store
    append_message(msg_data)
    
    from app.config import ENABLE_AGENT_MONITORING
    if ENABLE_AGENT_MONITORING:
        try:
            from app.swarm.communication_graph import record_message_flow
            record_message_flow(sender, receiver)
        except Exception as e:
            print(f"[MESSAGE BROKER] Error logging to communication graph: {e}")
            
    return msg_data

def broadcast(sender: str, content: str) -> List[Dict[str, Any]]:
    from app.swarm.agent_store import load_swarm_store
    store = load_swarm_store()
    agents = store.get("agents", {})
    
    sent_msgs = []
    # If no registered agents exist, default list of core agents to broadcast to
    receivers = list(agents.keys()) if agents else ["planner", "retrieval", "kg", "learning", "vqa", "grounding", "critic"]
    
    for receiver in receivers:
        if receiver != sender:
            msg = send_message(sender, receiver, content)
            sent_msgs.append(msg)
            
    return sent_msgs

def fetch_messages(receiver: str) -> List[Dict[str, Any]]:
    global _messages_db
    with _broker_lock:
        received = [msg for msg in _messages_db if msg["receiver"] == receiver]
        _messages_db = [msg for msg in _messages_db if msg["receiver"] != receiver]
    return received

def clear_broker():
    with _broker_lock:
        _messages_db.clear()
