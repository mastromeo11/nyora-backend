from datetime import datetime
from typing import List, Dict, Any
from app.embedding.text_embedder import embed_text
from app.simulation.simulation_store import (
    get_world_states,
    get_hypotheses,
    get_scenarios,
    get_simulations,
    get_counterfactuals,
    get_failure_forecasts
)
from app.simulation.world_model_cache import scenario_cache, state_cache, hypothesis_cache, simulation_cache
from app.config import ENABLE_WORLD_MODEL_CACHE

def dot_product(v1, v2) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))

def retrieve_simulation_context(query: str) -> dict:
    """
    Performs hybrid retrieval of relevant world models, scenarios, hypotheses, and forecasts.
    Score:
        score = 0.20 * similarity + 0.20 * confidence + 0.20 * importance + 0.20 * recency + 0.20 * success
    """
    # Try cache first if enabled
    if ENABLE_WORLD_MODEL_CACHE:
        cached_res = scenario_cache.get(query)
        if cached_res:
            return cached_res
            
    # Embed query
    query_emb = embed_text([query])[0]
    
    # 1. Retrieve & Score Scenarios
    scenarios = get_scenarios()
    scored_scenarios = []
    
    for scen in scenarios:
        # Load embedding or compute it (with persistence fallback)
        scen_emb = scen.embedding
        if scen_emb is None:
            # Bypassing recalculation where possible, but if missing, generate and save
            scen_emb = embed_text([scen.summary])[0]
            scen.embedding = scen_emb
            from app.simulation.simulation_store import append_scenario
            append_scenario(scen)
            
        sim = dot_product(query_emb, scen_emb)
        # Normalize sim to [0, 1]
        sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))
        
        confidence = min(1.0, max(0.0, scen.reinforcement_score))
        importance = scen.importance_score
        
        # Recency calculation
        recency = 1.0
        
        success = scen.success_probability
        
        score = 0.20 * sim + 0.20 * confidence + 0.20 * importance + 0.20 * recency + 0.20 * success
        scored_scenarios.append((scen, score))
        
    scored_scenarios.sort(key=lambda x: x[1], reverse=True)
    top_scenarios = [item[0] for item in scored_scenarios[:5]]
    
    # 2. Retrieve Hypotheses
    hypotheses = get_hypotheses()
    scored_hyps = []
    for hyp in hypotheses:
        # Cosine similarity using description
        hyp_emb = hyp.embedding if hasattr(hyp, "embedding") and getattr(hyp, "embedding") else embed_text([hyp.description])[0]
        if hasattr(hyp, "embedding") and getattr(hyp, "embedding") is None:
            hyp.embedding = hyp_emb
            from app.simulation.simulation_store import append_hypothesis
            append_hypothesis(hyp)
            
        sim = dot_product(query_emb, hyp_emb)
        sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))
        
        score = 0.4 * sim + 0.3 * hyp.confidence + 0.3 * (min(1.0, hyp.confirmation_count / 10.0))
        scored_hyps.append((hyp, score))
        
    scored_hyps.sort(key=lambda x: x[1], reverse=True)
    top_hyps = [item[0] for item in scored_hyps[:5]]
    
    # 3. Retrieve Failure Forecasts
    forecasts = get_failure_forecasts()
    # Simple term overlap or match
    matched_forecasts = []
    for f in forecasts:
        if f.failure_type.lower() in query.lower() or any(ent.lower() in query.lower() for ent in f.entities):
            matched_forecasts.append(f)
            
    # 4. Retrieve Counterfactuals
    counterfactuals = get_counterfactuals()
    matched_cfs = []
    for cf in counterfactuals:
        # Match base scenario or modified variable
        if cf.modified_variable.lower() in query.lower() or cf.alternative_outcome.lower() in query.lower():
            matched_cfs.append(cf)
            
    # 5. Retrieve Simulations
    simulations = get_simulations()
    matched_sims = []
    for sim in simulations:
        sim_emb = sim.embedding
        if sim_emb is None:
            # Standard simulation doesn't have text summary, so we use start + end state text or default
            sim_emb = embed_text([f"{sim.initial_state} to {sim.final_state}"])[0]
            sim.embedding = sim_emb
            from app.simulation.simulation_store import append_simulation
            append_simulation(sim)
            
        sim_score = dot_product(query_emb, sim_emb)
        sim_score = max(0.0, min(1.0, (sim_score + 1.0) / 2.0))
        matched_sims.append((sim, sim_score))
        
    matched_sims.sort(key=lambda x: x[1], reverse=True)
    top_sims = [item[0] for item in matched_sims[:5]]
    
    result = {
        "scenarios": [s.model_dump() for s in top_scenarios],
        "hypotheses": [h.model_dump() for h in top_hyps],
        "failure_forecasts": [f.model_dump() for f in matched_forecasts[:5]],
        "counterfactuals": [cf.model_dump() for cf in matched_cfs[:5]],
        "simulations": [sim.model_dump() for sim in top_sims]
    }
    
    if ENABLE_WORLD_MODEL_CACHE:
        scenario_cache.put(query, result)
        
    return result
