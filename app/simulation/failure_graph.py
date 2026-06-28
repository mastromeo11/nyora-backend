from typing import List, Dict, Any
from app.simulation.simulation_models import (
    FailureSimulationNode, PolicyFailureNode, FailureForecastNode
)

def build_failure_graph(
    failure_simulations: List[FailureSimulationNode],
    policy_failures: List[PolicyFailureNode],
    failure_forecasts: List[FailureForecastNode]
) -> Dict[str, Any]:
    """
    Builds a separate graph consisting purely of failure simulation paths,
    policy failures, and failure forecasts to isolate them from successful path models.
    """
    nodes = []
    edges = []
    existing_ids = set()
    
    def add_node(node_id: str, label: str, node_type: str, **kwargs):
        if node_id not in existing_ids:
            node_dict = {
                "id": node_id,
                "label": label,
                "type": node_type
            }
            node_dict.update(kwargs)
            nodes.append(node_dict)
            existing_ids.add(node_id)
            
    def add_edge(source: str, target: str, edge_type: str, **kwargs):
        if source == target:
            return
        edge_id = f"{source}_{edge_type}_{target}"
        if edge_id not in existing_ids:
            edge_dict = {
                "source": source,
                "target": target,
                "type": edge_type
            }
            edge_dict.update(kwargs)
            edges.append(edge_dict)
            existing_ids.add(edge_id)

    # 1. FailureSimulationNodes
    for f_sim in failure_simulations:
        add_node(
            f_sim.failure_simulation_id,
            f"Failure Sim: {f_sim.failure_type}",
            "failure_simulation_node",
            risk_score=f_sim.risk_score
        )
        
    # 2. PolicyFailureNodes
    for p_fail in policy_failures:
        add_node(
            p_fail.policy_id,
            f"Policy Failure: {p_fail.policy_id}",
            "policy_failure_node",
            failure_count=p_fail.failure_count
        )
        
        # Link policy failure to failure simulations if they share the policy or tool names
        for f_sim in failure_simulations:
            for tf in p_fail.tool_failures:
                if tf in f_sim.tool_failures:
                    add_edge(p_fail.policy_id, f_sim.failure_simulation_id, "policy_failure_to_sim")
                    break

    # 3. FailureForecastNodes
    for forecast in failure_forecasts:
        add_node(
            forecast.failure_forecast_id,
            f"Failure Forecast: {forecast.failure_type}",
            "failure_forecast_node",
            risk_score=forecast.risk_score
        )
        
        # Link forecast to failure simulations if they are of similar type
        for f_sim in failure_simulations:
            if (forecast.failure_type.lower() in f_sim.failure_type.lower() or 
                f_sim.failure_type.lower() in forecast.failure_type.lower()):
                add_edge(forecast.failure_forecast_id, f_sim.failure_simulation_id, "forecast_to_failure_simulation")

    return {
        "nodes": nodes,
        "edges": edges
    }
