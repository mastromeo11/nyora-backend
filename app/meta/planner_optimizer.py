from app.meta.meta_store import get_policies
from app.meta.strategy_memory_engine import match_similar_strategy

def select_planner(query: str) -> str:
    """
    Selects the optimal planner type (ReAct, Swarm, Retrieval-first, Simulation-first)
    based on matching strategy memory, history metrics, confidence, and query content.
    """
    # 1. Strategy memory check
    strategy = match_similar_strategy(query)
    if strategy and strategy.success_rate >= 0.5:
        return strategy.planner_id

    # 2. Heuristics based on query keywords (safety / intent routing)
    q = query.lower()
    if "simulate" in q or "what if" in q or "predict" in q or "suppose" in q:
        return "Simulation-first"
    if "swarm" in q or "coordination" in q or "collaborate" in q:
        return "Swarm"
    if "search" in q or "retrieve" in q or "documents" in q:
        return "Retrieval-first"

    # 3. Analyze general policy scores
    policies = get_policies()
    if policies:
        planner_scores = {}
        for p in policies:
            score = p.success_rate * p.confidence
            planner_scores[p.planner_type] = max(planner_scores.get(p.planner_type, 0.0), score)
        if planner_scores:
            best_planner = max(planner_scores, key=planner_scores.get)
            if planner_scores[best_planner] >= 0.5:
                return best_planner

    return "ReAct"  # Default
