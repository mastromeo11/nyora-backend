from app.swarm.agent_base import BaseSwarmAgent
from app.retrieval.grounding_validator import validate_grounding
from app.retrieval.evidence_models import EvidenceNode
from typing import Dict, Any, List

class GroundingAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="grounding",
            agent_name="Grounding Agent",
            role="factual_grounding_validation",
            capabilities=["claim_extraction", "grounding_check"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        answer = task.get("answer", "")
        evidence_dicts = task.get("evidence", [])
        
        evidence_nodes = []
        for ed in evidence_dicts:
            evidence_nodes.append(EvidenceNode(**ed))
            
        final_answer, report = validate_grounding(answer, evidence_nodes)
        self.write_mem("grounding_report", report)
        
        return {
            "status": "success",
            "final_answer": final_answer,
            "report": report
        }
