from app.swarm.agent_base import BaseSwarmAgent
from typing import Dict, Any, List
import re

class CriticAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="critic",
            agent_name="Critic Agent",
            role="output_criticism_and_contradiction_detection",
            capabilities=["contradiction_checking", "evidence_eval"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        retrieval_output = task.get("retrieval_output", "")
        kg_output = task.get("kg_output", "")
        
        contradiction_detected = False
        reason = ""
        
        v1 = re.findall(r"v\d+", retrieval_output.lower())
        v2 = re.findall(r"v\d+", kg_output.lower())
        if v1 and v2 and v1[0] != v2[0]:
            contradiction_detected = True
            reason = f"Version mismatch detected: Retrieval claims {v1[0]} while KG claims {v2[0]}."
            
        if (("cloud" in retrieval_output.lower() and "offline" in kg_output.lower()) or 
            ("offline" in retrieval_output.lower() and "cloud" in kg_output.lower())):
            contradiction_detected = True
            reason = "Hosting location mismatch detected: Retrieval claims cloud, KG/Local claims offline."
            
        self.write_mem("critic_report", {
            "contradiction_detected": contradiction_detected,
            "reason": reason
        })
        
        return {
            "status": "success",
            "contradiction_detected": contradiction_detected,
            "reason": reason
        }
