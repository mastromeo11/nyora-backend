from app.swarm.agent_base import BaseSwarmAgent
from app.retrieval.unified_retriever import retrieve_evidence
from typing import Dict, Any

class RetrievalAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="retrieval",
            agent_name="Retrieval Agent",
            role="document_retrieval",
            capabilities=["vector_search", "keyword_search"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        evidence = retrieve_evidence(query)
        serialized = [node.dict() for node in evidence]
        self.write_mem("retrieved_evidence", serialized)
        return {"status": "success", "evidence_count": len(evidence), "evidence": serialized}
