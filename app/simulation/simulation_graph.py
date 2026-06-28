from typing import List, Dict, Any
from app.simulation.simulation_models import (
    WorldStateNode, ScenarioNode, CounterfactualNode, SimulationNode, PolicyNode, FailureForecastNode
)

def extend_simulation_graph(
    base_graph: Dict[str, Any],
    world_states: List[WorldStateNode],
    scenarios: List[ScenarioNode],
    counterfactuals: List[CounterfactualNode],
    simulations: List[SimulationNode],
    policies: List[PolicyNode],
    forecasts: List[FailureForecastNode]
) -> Dict[str, Any]:
    """
    Extends the base Knowledge Graph dictionary with simulated nodes and edges.
    """
    nodes = base_graph.setdefault("nodes", [])
    edges = base_graph.setdefault("edges", [])
    
    existing_ids = {node["id"] for node in nodes}
    
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

    # 1. WorldStateNodes
    for ws in world_states:
        add_node(
            ws.world_state_id,
            f"World State: {ws.world_state_id[:8]}",
            "world_state_node",
            importance=ws.importance_score
        )

    # 2. ScenarioNodes
    for scen in scenarios:
        add_node(
            scen.scenario_id,
            f"Scenario: {scen.summary[:30]}...",
            "scenario_node",
            success_probability=scen.success_probability
        )
        # Edge: WorldStateNode -> ScenarioNode or ScenarioNode -> ScenarioNode
        # Check if parent is a world state or scenario
        add_edge(scen.parent_state, scen.scenario_id, "parent_to_scenario")

    # 3. CounterfactualNodes
    for cf in counterfactuals:
        add_node(
            cf.counterfactual_id,
            f"Counterfactual: {cf.modified_variable}",
            "counterfactual_node",
            confidence=cf.confidence
        )
        # Edge: ScenarioNode -> CounterfactualNode
        add_edge(cf.base_scenario, cf.counterfactual_id, "scenario_to_counterfactual")

    # 4. SimulationNodes
    for sim in simulations:
        add_node(
            sim.simulation_id,
            f"Simulation: {sim.simulation_id[:8]}",
            "simulation_node",
            score=sim.score
        )
        # Edge: ScenarioNode -> SimulationNode (for all scenarios in the chain)
        for scen_id in sim.scenario_chain:
            add_edge(scen_id, sim.simulation_id, "scenario_to_simulation")

    # 5. PolicyNodes
    for pol in policies:
        add_node(
            pol.policy_id,
            f"Policy: {pol.policy_id}",
            "policy_node",
            success_rate=pol.success_rate
        )
        # Edge: PolicyNode -> SimulationNode (if simulation trace aligns with this policy)
        for sim in simulations:
            if pol.policy_id in sim.planner_trace_ids:
                add_edge(pol.policy_id, sim.simulation_id, "policy_to_simulation")

    # 6. FailureForecastNodes
    for f in forecasts:
        add_node(
            f.failure_forecast_id,
            f"Forecast: {f.failure_type}",
            "failure_forecast_node",
            risk_score=f.risk_score
        )
        # Edge: FailureForecastNode -> ScenarioNode (link to scenarios mentioning the failure risk)
        for scen in scenarios:
            if f.failure_type.lower() in scen.summary.lower():
                add_edge(f.failure_forecast_id, scen.scenario_id, "forecast_to_scenario")

    return {
        "nodes": nodes,
        "edges": edges
    }
