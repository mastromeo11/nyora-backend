from typing import List, Dict, Any, Set
from app.learning.learning_models import (
    PatternNode,
    CorrectionNode,
    FeedbackNode,
    QueryClusterNode,
    FailurePatternNode
)
from app.config import MAX_LEARNING_DEPTH, MAX_PATTERN_CHAIN

def extend_learning_graph(
    base_graph: Dict[str, Any],
    patterns: List[PatternNode],
    corrections: List[CorrectionNode],
    feedbacks: List[FeedbackNode],
    clusters: List[QueryClusterNode],
    failures: List[FailurePatternNode]
) -> Dict[str, Any]:
    """
    Extends the Knowledge Graph with learning nodes and edges.
    Applies loop protection constraints.
    """
    nodes = base_graph.get("nodes", [])
    edges = base_graph.get("edges", [])
    
    existing_ids = {node["id"] for node in nodes}
    
    # helper to add nodes safely
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
            
    # helper to add edges safely
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

    # 1. Add PatternNodes (PatternNode -> EntityNode)
    for pat in patterns[:MAX_PATTERN_CHAIN]:
        add_node(
            pat.pattern_id, 
            f"Pattern: {pat.signature}", 
            "pattern_node", 
            confidence=pat.confidence,
            frequency=pat.frequency
        )
        for ent in pat.supporting_entities:
            ent_id = f"entity_{ent}"
            # Add edge PatternNode -> EntityNode
            add_edge(pat.pattern_id, ent_id, "pattern_to_entity")

    # 2. Add CorrectionNodes (CorrectionNode -> EvidenceNode)
    for corr in corrections[:MAX_PATTERN_CHAIN]:
        add_node(
            corr.correction_id,
            f"Correction: {corr.reason[:30]}...",
            "correction_node",
            confidence=corr.confidence
        )
        for ev_id in corr.evidence_ids:
            # Add edge CorrectionNode -> EvidenceNode
            add_edge(corr.correction_id, ev_id, "correction_to_evidence")

    # 3. Add FeedbackNodes (FeedbackNode -> PatternNode)
    for fb in feedbacks[:MAX_PATTERN_CHAIN]:
        add_node(
            fb.feedback_id,
            f"Feedback: {fb.feedback_type}",
            "feedback_node",
            confidence=fb.confidence
        )
        # Link feedback to pattern nodes sharing intent
        for pat in patterns[:MAX_PATTERN_CHAIN]:
            add_edge(fb.feedback_id, pat.pattern_id, "feedback_to_pattern")

    # 4. Add QueryClusterNodes (QueryClusterNode -> EntityNode)
    for clust in clusters[:MAX_PATTERN_CHAIN]:
        add_node(
            clust.cluster_id,
            f"Cluster: {clust.cluster_center_query[:25]}...",
            "cluster_node",
            importance=clust.importance_score
        )
        for ent in clust.entities:
            ent_id = f"entity_{ent}"
            # Add edge QueryClusterNode -> EntityNode
            add_edge(clust.cluster_id, ent_id, "cluster_to_entity")

    # 5. Add FailurePatternNodes (FailurePatternNode -> ReflectionNode)
    for fail in failures[:MAX_PATTERN_CHAIN]:
        add_node(
            fail.failure_pattern_id,
            f"Failure: {fail.failure_type}",
            "failure_pattern_node",
            confidence=fail.confidence
        )
        # Link to matching reflection nodes if they exist in base graph
        for node in list(nodes):
            if node.get("type") == "reflection_node":
                add_edge(fail.failure_pattern_id, node["id"], "failure_to_reflection")

    return {
        "nodes": nodes,
        "edges": edges
    }
