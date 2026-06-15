from app.swarm.agent_base import BaseSwarmAgent
from app.learning.learning_retriever import retrieve_learning_context
from typing import Dict, Any

class LearningAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="learning",
            agent_name="Learning Agent",
            role="self_learning_and_correction_retrieval",
            capabilities=["pattern_discovery", "failure_matching"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        learning_context = retrieve_learning_context(query)
        self.write_mem("learning_context", learning_context)
        return {"status": "success", "learning_context": learning_context}
