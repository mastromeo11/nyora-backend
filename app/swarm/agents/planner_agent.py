from app.swarm.agent_base import BaseSwarmAgent
from typing import Dict, Any

class PlannerAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="planner",
            agent_name="Planner Agent",
            role="decomposition_and_delegation",
            capabilities=["planning", "delegation"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        self.write_mem("query_goal", {"query": query, "status": "planning"})
        
        delegations = [
            {"receiver": "retrieval", "task": {"query": query, "type": "retrieve"}},
            {"receiver": "kg", "task": {"query": query, "type": "kg_search"}},
            {"receiver": "learning", "task": {"query": query, "type": "learning_search"}}
        ]
        
        self.write_mem("delegated_tasks", delegations)
        return {"status": "success", "delegations": delegations}
