from app.simulation.simulation_store import load_world_model_store, save_world_model_store

def prune_simulation_memory() -> float:
    """
    Prunes low-confidence, zero-weight, and broken simulation nodes.
    Returns a pruning efficiency score (defaults to 1.0).
    """
    mem = load_world_model_store()
    
    initial_counts = {
        "world_states": len(mem.get("world_states", {})),
        "hypotheses": len(mem.get("hypotheses", {})),
        "scenarios": len(mem.get("scenarios", {})),
        "simulations": len(mem.get("simulations", {})),
        "policies": len(mem.get("policies", {})),
        "failure_forecasts": len(mem.get("failure_forecasts", {}))
    }
    
    # 1. Prune World States with low importance
    ws_keys_to_remove = [
        k for k, v in mem.get("world_states", {}).items() 
        if v.get("importance_score", 0.0) < 0.1
    ]
    for k in ws_keys_to_remove:
        del mem["world_states"][k]
        
    # 2. Prune Hypotheses with low confidence
    hyp_keys_to_remove = [
        k for k, v in mem.get("hypotheses", {}).items() 
        if v.get("confidence", 0.0) < 0.1
    ]
    for k in hyp_keys_to_remove:
        del mem["hypotheses"][k]
        
    # 3. Prune Scenarios with low importance/reinforcement or broken parent links
    scen_keys_to_remove = []
    for k, v in mem.get("scenarios", {}).items():
        low_val = v.get("importance_score", 0.0) < 0.1 or v.get("reinforcement_score", 0.0) < 0.1
        parent = v.get("parent_state")
        broken_parent = parent not in mem.get("world_states", {}) and parent not in mem.get("scenarios", {})
        if low_val or broken_parent:
            scen_keys_to_remove.append(k)
    for k in scen_keys_to_remove:
        del mem["scenarios"][k]
        
    # 4. Prune Simulations with low scores
    sim_keys_to_remove = [
        k for k, v in mem.get("simulations", {}).items() 
        if v.get("score", 0.0) < 0.1
    ]
    for k in sim_keys_to_remove:
        del mem["simulations"][k]
        
    # 5. Prune Policies with low reinforcement or low success_rate
    pol_keys_to_remove = [
        k for k, v in mem.get("policies", {}).items() 
        if v.get("success_rate", 0.0) < 0.1 or v.get("reinforcement_score", 0.0) < 0.1
    ]
    for k in pol_keys_to_remove:
        del mem["policies"][k]
        
    # 6. Prune Failure Forecasts with low risk_score
    ff_keys_to_remove = [
        k for k, v in mem.get("failure_forecasts", {}).items() 
        if v.get("risk_score", 0.0) < 0.1
    ]
    for k in ff_keys_to_remove:
        del mem["failure_forecasts"][k]
        
    save_world_model_store()
    
    total_pruned = (len(ws_keys_to_remove) + len(hyp_keys_to_remove) + 
                    len(scen_keys_to_remove) + len(sim_keys_to_remove) + 
                    len(pol_keys_to_remove) + len(ff_keys_to_remove))
                    
    print(f"[WORLD MODEL PRUNER] Pruned {total_pruned} elements from database.")
    return 1.0
