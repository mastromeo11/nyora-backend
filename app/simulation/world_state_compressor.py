import uuid
from datetime import datetime
from typing import List, Optional
from app.simulation.simulation_models import WorldStateNode
from app.simulation.simulation_store import append_world_state
from app.retrieval.graph_store import get_entities
from app.episodic.episodic_store import get_episodes, get_experiences, get_failure_replays
from app.learning.learning_store import get_feedback, get_failure_patterns

def compress_current_world_state(
    summary_text: Optional[str] = None,
    embedding: Optional[List[float]] = None
) -> WorldStateNode:
    """
    Compresses current Knowledge Graph, Episodic memory, and Self-Learning nodes into a single WorldStateNode.
    Populates distributions of entities, tools, agents, and failures.
    """
    # 1. Entity distribution from KG
    entity_dist = {}
    try:
        for ent in get_entities():
            entity_dist[ent.canonical_name] = ent.mentions
    except Exception:
        pass
        
    # 2. Tool & Agent distributions from Episodic memory experiences
    tool_dist = {}
    agent_dist = {}
    try:
        for exp in get_experiences():
            for tool in exp.tools_used:
                tool_dist[tool] = tool_dist.get(tool, 0) + 1
            for agent in exp.agent_trace_ids:
                agent_dist[agent] = agent_dist.get(agent, 0) + 1
    except Exception:
        pass
        
    # 3. Failure distribution from self-learning and episodic failure records
    failure_dist = {}
    try:
        for fp in get_failure_patterns():
            failure_dist[fp.failure_type] = failure_dist.get(fp.failure_type, 0) + fp.timeout_count
        for fr in get_failure_replays():
            failure_dist[fr.failure_type] = failure_dist.get(fr.failure_type, 0) + fr.frequency
    except Exception:
        pass
        
    now_str = datetime.utcnow().isoformat()
    
    if not summary_text:
        summary_text = (
            f"World State at {now_str}. "
            f"Entities count: {len(entity_dist)}, Tools observed: {len(tool_dist)}, "
            f"Failures recorded: {sum(failure_dist.values())}."
        )
        
    node = WorldStateNode(
        world_state_id=f"ws_{uuid.uuid4().hex[:8]}",
        entities=list(entity_dist.keys()),
        relations=[],  # Can be expanded if needed
        timestamp=now_str,
        importance_score=0.8,
        confidence=1.0,
        summary=summary_text,
        embedding=embedding,
        entity_distribution=entity_dist,
        tool_distribution=tool_dist,
        agent_distribution=agent_dist,
        failure_distribution=failure_dist
    )
    
    append_world_state(node)
    return node
