from app.simulation.simulation_store import load_world_model_store, save_world_model_store

def decay_simulation_memory():
    """
    Decays importance, confidence, and probability scores of stored world model nodes.
    Multipliers:
        confidence *= 0.99
        importance *= 0.98
        probability *= 0.99
    """
    mem = load_world_model_store()
    
    # 1. World States
    for ws in mem.get("world_states", {}).values():
        ws["confidence"] = max(0.0, ws.get("confidence", 1.0) * 0.99)
        ws["importance_score"] = max(0.0, ws.get("importance_score", 0.0) * 0.98)
        
    # 2. Hypotheses
    for hyp in mem.get("hypotheses", {}).values():
        hyp["confidence"] = max(0.0, hyp.get("confidence", 1.0) * 0.99)
        
    # 3. Scenarios
    for scen in mem.get("scenarios", {}).values():
        scen["success_probability"] = max(0.0, scen.get("success_probability", 1.0) * 0.99)
        scen["importance_score"] = max(0.0, scen.get("importance_score", 0.0) * 0.98)
        
    # 4. Simulations
    for sim in mem.get("simulations", {}).values():
        sim["score"] = max(0.0, sim.get("score", 0.0) * 0.98)
        
    # 5. Policies
    for pol in mem.get("policies", {}).values():
        pol["confidence"] = max(0.0, pol.get("confidence", 1.0) * 0.99)
        pol["average_confidence"] = max(0.0, pol.get("average_confidence", 1.0) * 0.99)
        
    # 6. Failure Forecasts
    for ff in mem.get("failure_forecasts", {}).values():
        ff["risk_score"] = max(0.0, ff.get("risk_score", 0.0) * 0.99)
        ff["probability"] = max(0.0, ff.get("probability", 0.0) * 0.99)
        
    save_world_model_store()
