from app.simulation.simulation_store import append_simulation, get_simulations

def reinforce_simulation_node(simulation_id: str, success: bool, alpha: float = 0.1):
    """
    Reinforces simulation nodes.
    If success (predicted outcome matches final results):
       - Increment reinforcement_score (frequency/success counter)
       - Add confidence weight alpha to score
    If success is False (prediction was wrong):
       - Decay score (confidence) by multiplying by (1 - alpha)
    """
    sims = get_simulations()
    match = None
    for sim in sims:
        if sim.simulation_id == simulation_id:
            match = sim
            break
            
    if not match:
        return None
        
    if success:
        match.reinforcement_score += 1.0
        match.score = min(1.0, match.score + alpha)
    else:
        match.score = max(0.0, match.score * (1.0 - alpha))
        
    append_simulation(match)
    return match
