from app.swarm.agent_base import BaseSwarmAgent
from app.retrieval.knowledge_retriever import retrieve_knowledge
from typing import Dict, Any

class KGAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="kg",
            agent_name="Knowledge Graph Agent",
            role="graph_semantic_reasoning",
            capabilities=["multi_hop_traversal", "entity_extraction"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        kg_context = retrieve_knowledge(query, "default_session")
        self.write_mem("kg_context", kg_context)
        return {"status": "success", "kg_context": kg_context}
