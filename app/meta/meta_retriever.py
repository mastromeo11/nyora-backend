from typing import List, Dict, Any
from app.meta.meta_store import (
    get_tools, get_policies, get_strategies, get_reflections, get_replays
)
from app.meta.meta_models import (
    ToolLearningNode, PlannerPolicyNode, StrategyNode, MetaReflectionNode, PolicyReplayNode
)
from app.embedding.text_embedder import embed_text
from app.config import (
    MAX_POLICY_DEPTH, MAX_TOTAL_POLICIES_VISITED, MAX_STRATEGIES_VISITED
)

def retrieve_meta_context(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Performs hybrid cosine-similarity retrieval over:
    - ToolLearningNodes
    - PlannerPolicyNodes
    - StrategyNodes
    - MetaReflectionNodes
    - PolicyReplayNodes
    Enforces loop protection traversal bounds.
    """
    try:
        q_emb = embed_text([query])[0]
    except Exception:
        q_emb = [0.0] * 384

    # Keep track of visited keys to prevent duplicate checks/loops
    visited_policy_ids = set()
    visited_strategy_ids = set()
    visited_replay_ids = set()
    visited_tool_ids = set()

    # 1. Retrieve & Rank Tool Learning Nodes
    tools = get_tools()
    scored_tools = []
    for t in tools:
        if len(visited_tool_ids) >= MAX_TOTAL_POLICIES_VISITED:
            break
        visited_tool_ids.add(t.tool_id)

        try:
            t_emb = embed_text([t.tool_name])[0]
            dot_prod = sum(a * b for a, b in zip(q_emb, t_emb))
            mag_q = sum(a * a for a in q_emb) ** 0.5
            mag_t = sum(b * b for b in t_emb) ** 0.5
            sim = dot_prod / (mag_q * mag_t + 1e-9)
        except Exception:
            sim = 0.5

        freq_score = min(t.frequency / 10.0, 1.0)
        score = (
            0.25 * sim +
            0.20 * t.success_rate +
            0.20 * t.confidence +
            0.15 * t.importance_score +
            0.10 * 1.0 +  # recency default
            0.10 * freq_score
        )
        scored_tools.append((score, t))
    scored_tools.sort(key=lambda x: x[0], reverse=True)

    # 2. Retrieve & Rank Planner Policies
    policies = get_policies()
    scored_policies = []
    for p in policies:
        if len(visited_policy_ids) >= MAX_TOTAL_POLICIES_VISITED:
            break
        visited_policy_ids.add(p.policy_id)

        try:
            p_emb = embed_text([p.signature])[0]
            dot_prod = sum(a * b for a, b in zip(q_emb, p_emb))
            mag_q = sum(a * a for a in q_emb) ** 0.5
            mag_p = sum(b * b for b in p_emb) ** 0.5
            sim = dot_prod / (mag_q * mag_p + 1e-9)
        except Exception:
            sim = 0.5

        freq_score = min(p.frequency / 10.0, 1.0)
        score = (
            0.25 * sim +
            0.20 * p.success_rate +
            0.20 * p.confidence +
            0.15 * p.importance +
            0.10 * p.recency +
            0.10 * freq_score
        )
        scored_policies.append((score, p))
    scored_policies.sort(key=lambda x: x[0], reverse=True)

    # 3. Retrieve & Rank Strategies
    strategies = get_strategies()
    scored_strategies = []
    for s in strategies:
        if len(visited_strategy_ids) >= MAX_STRATEGIES_VISITED:
            break
        visited_strategy_ids.add(s.strategy_id)

        try:
            s_emb = embed_text([s.query_pattern])[0]
            dot_prod = sum(a * b for a, b in zip(q_emb, s_emb))
            mag_q = sum(a * a for a in q_emb) ** 0.5
            mag_s = sum(b * b for b in s_emb) ** 0.5
            sim = dot_prod / (mag_q * mag_s + 1e-9)
        except Exception:
            sim = 0.5

        freq_score = min(s.frequency if hasattr(s, "frequency") else 1 / 10.0, 1.0)
        score = (
            0.25 * sim +
            0.20 * s.success_rate +
            0.20 * s.confidence +
            0.15 * 1.0 +  # importance default
            0.10 * 1.0 +  # recency default
            0.10 * freq_score
        )
        scored_strategies.append((score, s))
    scored_strategies.sort(key=lambda x: x[0], reverse=True)

    # 4. Retrieve & Rank Reflections
    reflections = get_reflections()
    scored_reflections = []
    for r in reflections:
        try:
            r_emb = embed_text([r.reflection_summary])[0]
            dot_prod = sum(a * b for a, b in zip(q_emb, r_emb))
            mag_q = sum(a * a for a in q_emb) ** 0.5
            mag_r = sum(b * b for b in r_emb) ** 0.5
            sim = dot_prod / (mag_q * mag_r + 1e-9)
        except Exception:
            sim = 0.5

        score = sim
        scored_reflections.append((score, r))
    scored_reflections.sort(key=lambda x: x[0], reverse=True)

    # 5. Retrieve & Rank Policy Replays (limit depth to MAX_POLICY_DEPTH)
    replays = get_replays()
    scored_replays = []
    for idx, rep in enumerate(replays):
        if idx >= MAX_POLICY_DEPTH:
            break
        visited_replay_ids.add(rep.replay_id)

        # Basic similarity match
        sim = rep.similarity
        score = (
            0.25 * sim +
            0.20 * (rep.success_count / max(rep.frequency, 1)) +
            0.20 * 1.0 +  # confidence default
            0.15 * 1.0 +  # importance default
            0.10 * 1.0 +  # recency default
            0.10 * min(rep.frequency / 10.0, 1.0)
        )
        scored_replays.append((score, rep))
    scored_replays.sort(key=lambda x: x[0], reverse=True)

    return {
        "tools": [item[1] for item in scored_tools[:limit]],
        "policies": [item[1] for item in scored_policies[:limit]],
        "strategies": [item[1] for item in scored_strategies[:limit]],
        "reflections": [item[1] for item in scored_reflections[:limit]],
        "replays": [item[1] for item in scored_replays[:limit]]
    }
