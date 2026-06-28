import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.simulation.simulation_models import ScenarioSummaryNode, ScenarioNode, SimulationArchiveNode
from app.simulation.simulation_store import (
    append_scenario_summary, get_scenarios, get_simulations, 
    get_scenario_summaries, append_simulation_archive
)
from app.llm.ollama_client import ollama_client

def compress_scenario_chain_if_needed(scenario_ids: List[str], parent_simulation_id: str) -> Optional[ScenarioSummaryNode]:
    """
    Compresses a chain of scenarios when length exceeds 20.
    Produces ScenarioSummaryNode using LLM summarizing or template fallback.
    """
    if len(scenario_ids) <= 20:
        return None
        
    scenarios_list = get_scenarios()
    scenarios_map = {s.scenario_id: s for s in scenarios_list}
    
    chain_scenarios: List[ScenarioNode] = []
    for sid in scenario_ids:
        if sid in scenarios_map:
            chain_scenarios.append(scenarios_map[sid])
            
    if not chain_scenarios:
        return None
        
    # Count metrics
    successes = sum(1 for s in chain_scenarios if s.success_probability >= 0.5)
    failures = len(chain_scenarios) - successes
    
    # Collect entities and events
    all_entities = []
    events = []
    for idx, s in enumerate(chain_scenarios):
        events.append(f"Step {idx+1}: {s.summary}")
        
    summary_text = ""
    # LLM Compression
    prompt = (
        f"Summarize the following sequence of execution simulation branches:\n"
        + "\n".join(events) +
        f"\n\nSuccesses: {successes}, Failures: {failures}."
        f"\nProvide a short summary without any chain-of-thought details."
    )
    
    try:
        summary_text = ollama_client.generate_response(
            query=prompt,
            context="You are a system simulation summarizing daemon."
        )
    except Exception as e:
        print(f"[SCENARIO COMPRESSION] LLM summarization failed: {e}. Falling back to template summary.")
        # Template Fallback
        summary_text = (
            f"Scenario simulation path containing {len(chain_scenarios)} branches. "
            f"Successfully executed {successes} routes, encountered {failures} issues."
        )
        
    node = ScenarioSummaryNode(
        summary_id=f"scen_sum_{uuid.uuid4().hex[:8]}",
        scenario_id=parent_simulation_id,
        summary=summary_text,
        major_events=events[:5],  # Keep first 5 events as major
        milestones=[s.summary for s in chain_scenarios if s.importance_score >= 0.7],
        successes=successes,
        failures=failures,
        entities=all_entities
    )
    
    append_scenario_summary(node)
    return node

def archive_simulations_if_needed() -> Optional[SimulationArchiveNode]:
    """
    Hierarchical archiving: when simulation count exceeds 100, archive
    raw scenario chains and summaries into SimulationArchiveNode records.
    """
    simulations = get_simulations()
    if len(simulations) > 100:
        sim_ids = [s.simulation_id for s in simulations]
        summaries = get_scenario_summaries()
        summary_texts = [sum_node.summary for sum_node in summaries]
        summary_text = f"Archived {len(sim_ids)} simulations. Sample summaries: " + "; ".join(summary_texts[:5])
        
        archive_node = SimulationArchiveNode(
            archive_id=f"arch_{uuid.uuid4().hex[:8]}",
            simulation_ids=sim_ids,
            summary_text=summary_text,
            milestones=["Archived simulation count limit exceeded"],
            timestamp=datetime.utcnow().isoformat()
        )
        append_simulation_archive(archive_node)
        return archive_node
    return None
