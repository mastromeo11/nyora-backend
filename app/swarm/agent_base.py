import time
from typing import List, Dict, Any, Optional
from app.swarm.agent_store import append_agent
from app.swarm.message_broker import send_message, fetch_messages
from app.swarm.shared_memory import read_shared_memory, write_shared_memory
from app.swarm.agent_monitor import record_agent_execution

class BaseSwarmAgent:
    def __init__(self, agent_id: str, agent_name: str, role: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.capabilities = capabilities
        
        append_agent({
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role,
            "capabilities": self.capabilities,
            "registered_at": time.time()
        })

    def send_msg(self, receiver: str, content: str) -> dict:
        return send_message(self.agent_id, receiver, content)

    def receive_msgs(self) -> List[dict]:
        return fetch_messages(self.agent_id)

    def read_mem(self, key: str) -> Optional[dict]:
        return read_shared_memory(key)

    def write_mem(self, key: str, value: Any) -> dict:
        return write_shared_memory(key, value, self.agent_id)

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        t_start = time.time()
        success = True
        try:
            res = self._run(task)
            return res
        except Exception as e:
            success = False
            raise e
        finally:
            latency = (time.time() - t_start) * 1000.0
            record_agent_execution(self.agent_id, success=success, latency_ms=latency)

    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "result": "base execution"}
