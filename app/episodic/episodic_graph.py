from typing import List, Dict, Any
from app.episodic.episodic_models import (
    EpisodeNode, ExperienceNode, ReplayNode, TemporalChainNode, MemoryClusterNode, FailureReplayNode
)

def extend_episodic_graph(
    base_graph: Dict[str, Any],
    episodes: List[EpisodeNode],
    experiences: List[ExperienceNode],
    replays: List[ReplayNode],
    chains: List[TemporalChainNode],
    clusters: List[MemoryClusterNode],
    failures: List[FailureReplayNode]
) -> Dict[str, Any]:
    """
    Extends the Knowledge Graph representation with episodic Nodes and Edges.
    """
    nodes = base_graph.get("nodes", [])
    edges = base_graph.get("edges", [])
    
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

    # 1. Add EpisodeNodes
    for ep in episodes:
        add_node(
            ep.episode_id,
            f"Episode: {ep.query[:30]}...",
            "episode_node",
            importance=ep.importance_score
        )
        for ent in ep.entities:
            ent_id = f"entity_{ent}"
            add_edge(ep.episode_id, ent_id, "episode_to_entity")

    # 2. Add ExperienceNodes & EpisodeNode -> ExperienceNode edges
    exp_by_episode = {exp.episode_id: exp for exp in experiences}
    for ep in episodes:
        exp = exp_by_episode.get(ep.episode_id)
        if exp:
            add_node(
                exp.experience_id,
                f"Experience: {', '.join(exp.tools_used[:3]) if exp.tools_used else 'General'}",
                "experience_node",
                success=exp.success_status
            )
            add_edge(ep.episode_id, exp.experience_id, "episode_to_experience")

    # 3. Add ReplayNodes & ReplayNode -> EpisodeNode edges
    for rep in replays:
        add_node(
            rep.replay_id,
            f"Replay: {rep.similarity_score:.2f}",
            "replay_node",
            frequency=rep.frequency
        )
        add_edge(rep.replay_id, rep.source_episode, "replay_to_source")
        add_edge(rep.replay_id, rep.target_episode, "replay_to_target")

    # 4. Add TemporalChainNodes & TemporalChainNode -> EpisodeNode edges
    for ch in chains:
        add_node(
            ch.chain_id,
            f"Chain: {ch.chain_id[:8]}",
            "temporal_chain_node",
            importance=ch.chain_importance
        )
        for ep_id in ch.episode_ids:
            add_edge(ch.chain_id, ep_id, "chain_to_episode")

    # 5. Add MemoryClusterNodes & MemoryClusterNode -> EpisodeNode edges
    for cl in clusters:
        add_node(
            cl.cluster_id,
            f"Cluster: {cl.cluster_center_query[:20]}...",
            "memory_cluster_node",
            importance=cl.importance_score
        )
        for ep_id in cl.episodes:
            add_edge(cl.cluster_id, ep_id, "cluster_to_episode")

    # 6. Add FailureReplayNodes & FailureReplayNode -> ReflectionNode edges
    for fail in failures:
        add_node(
            fail.failure_replay_id,
            f"Failure Replay: {fail.failure_type}",
            "failure_replay_node",
            frequency=fail.frequency
        )
        # Scan for existing reflection nodes in base graph to build linkage
        for n in list(nodes):
            if n.get("type") == "reflection_node":
                add_edge(fail.failure_replay_id, n["id"], "failure_to_reflection")

    return {
        "nodes": nodes,
        "edges": edges
    }
