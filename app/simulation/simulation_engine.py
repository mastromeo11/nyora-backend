import uuid
from datetime import datetime
from typing import List, Optional, Set
from app.simulation.simulation_models import SimulationNode, ScenarioNode
from app.simulation.simulation_store import append_simulation, get_simulations, get_scenarios
from app.config import MAX_SIMULATION_DEPTH, MAX_TOTAL_STATES_VISITED, MAX_TOTAL_BRANCHES_VISITED

def record_simulation_run(
    initial_state_id: str,
    final_state_id: str,
    scenario_chain: List[str],
    score: float,
    planner_trace_ids: List[str] = None,
    critic_trace_ids: List[str] = None,
    consensus_trace_ids: List[str] = None,
    agent_ids: List[str] = None,
    tool_ids: List[str] = None,
    embedding: List[float] = None
) -> SimulationNode:
    """
    Creates and appends a SimulationNode to the database.
    Reinforces confidence / reinforcement scores if similar simulation already exists.
    """
    planner_trace_ids = planner_trace_ids or []
    critic_trace_ids = critic_trace_ids or []
    consensus_trace_ids = consensus_trace_ids or []
    agent_ids = agent_ids or []
    tool_ids = tool_ids or []
    
    # Check if a matching simulation already exists
    existing = get_simulations()
    match = None
    for sim in existing:
        if sim.initial_state == initial_state_id and sim.final_state == final_state_id:
            match = sim
            break
            
    now_str = datetime.utcnow().isoformat()
    if match:
        match.score = 0.7 * match.score + 0.3 * score
        match.reinforcement_score += 1.0
        match.timestamp = now_str
        node_to_save = match
    else:
        node_to_save = SimulationNode(
            simulation_id=f"sim_{uuid.uuid4().hex[:8]}",
            initial_state=initial_state_id,
            final_state=final_state_id,
            scenario_chain=scenario_chain,
            score=score,
            timestamp=now_str,
            planner_trace_ids=planner_trace_ids,
            critic_trace_ids=critic_trace_ids,
            consensus_trace_ids=consensus_trace_ids,
            agent_ids=agent_ids,
            tool_ids=tool_ids,
            embedding=embedding,
            reinforcement_score=1.0
        )
        
    append_simulation(node_to_save)
    
    # Hierarchical archiving check
    from app.simulation.scenario_compression_engine import archive_simulations_if_needed
    archive_simulations_if_needed()
    
    return node_to_save

def traverse_simulation_paths(
    start_state_id: str,
    max_depth: int = MAX_SIMULATION_DEPTH,
    max_visited: int = MAX_TOTAL_STATES_VISITED,
    max_branches: int = MAX_TOTAL_BRANCHES_VISITED
) -> List[List[ScenarioNode]]:
    """
    Traverses branching scenarios from a starting state.
    Uses depth limits, total state limits, and branch limits to prevent graph explosions.
    """
    all_scenarios = get_scenarios()
    # Map parent_state to child scenarios
    scenario_map = {}
    for scen in all_scenarios:
        scenario_map.setdefault(scen.parent_state, []).append(scen)
        
    visited_state_ids: Set[str] = set()
    visited_branch_ids: Set[str] = set()
    visited_scenario_ids: Set[str] = set()
    visited_policy_ids: Set[str] = set()
    
    paths: List[List[ScenarioNode]] = []
    
    def dfs(current_state_id: str, current_path: List[ScenarioNode], depth: int):
        if len(visited_state_ids) >= max_visited or depth > max_depth or len(visited_branch_ids) >= max_branches:
            return
            
        visited_state_ids.add(current_state_id)
        
        children = scenario_map.get(current_state_id, [])
        if not children:
            if current_path:
                paths.append(list(current_path))
            return
            
        for child in children:
            branch_key = f"{current_state_id}->{child.scenario_id}"
            if branch_key in visited_branch_ids:
                continue
            if len(visited_branch_ids) >= max_branches:
                break
                
            visited_branch_ids.add(branch_key)
            
            if child.scenario_id in visited_scenario_ids:
                continue
            visited_scenario_ids.add(child.scenario_id)
            
            if "policy_" in child.scenario_id:
                visited_policy_ids.add(child.scenario_id)
                
            current_path.append(child)
            dfs(child.scenario_id, current_path, depth + 1)
            current_path.pop()
            
    dfs(start_state_id, [], 1)
    return paths
