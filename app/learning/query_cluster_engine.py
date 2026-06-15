import uuid
from datetime import datetime
from typing import List, Set, Dict, Any, Optional
from app.embedding.text_embedder import embed_text
from app.learning.learning_models import QueryClusterNode
from app.learning.learning_store import get_clusters, save_clusters
from app.retrieval.entity_alias_registry import get_canonical_entities
import numpy as np

def _get_vector(text: str) -> List[float]:
    try:
        return embed_text([text])[0]
    except Exception as e:
        print(f"[CLUSTER ENGINE] Embedding error: {e}")
        return [0.0] * 384

def _cosine_sim(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    return float(np.dot(v1, v2))

def cluster_query(query: str, success: bool = True):
    """
    Assigns the query to an existing semantic cluster using vector similarity,
    or initializes a new QueryClusterNode.
    """
    query_emb = _get_vector(query)
    
    clusters = get_clusters()
    matched_cluster: Optional[QueryClusterNode] = None
    best_sim = -1.0
    
    # 1. Search for matching cluster
    for cluster in clusters:
        center_emb = _get_vector(cluster.cluster_center_query)
        sim = _cosine_sim(query_emb, center_emb)
        if sim >= 0.85:  # high similarity threshold
            if sim > best_sim:
                best_sim = sim
                matched_cluster = cluster

    now_str = datetime.utcnow().isoformat()
    ents = list(get_canonical_entities(query))
    
    if matched_cluster:
        # Update existing cluster
        matched_cluster.queries = list(set(matched_cluster.queries + [query]))
        matched_cluster.entities = list(set(matched_cluster.entities + ents))
        matched_cluster.frequency += 1
        
        # Success rate recalculation
        total_runs = matched_cluster.frequency
        success_runs = (matched_cluster.success_rate * (total_runs - 1)) + (1.0 if success else 0.0)
        matched_cluster.success_rate = round(success_runs / total_runs, 4)
        
        # Compute importance:
        # importance = 0.4 * frequency_score + 0.3 * success_rate + 0.3 * recency
        freq_score = min(matched_cluster.frequency / 10.0, 1.0)
        recency = 1.0
        
        matched_cluster.importance_score = round(
            0.4 * freq_score + 0.3 * matched_cluster.success_rate + 0.3 * recency,
            4
        )
        
        # Simple entity distribution update
        dist = matched_cluster.entity_distribution or {}
        for ent in ents:
            dist[ent] = dist.get(ent, 0.0) + 1.0
        # Normalize
        total_weight = sum(dist.values())
        if total_weight > 0:
            matched_cluster.entity_distribution = {k: round(v / total_weight, 4) for k, v in dist.items()}
            
    else:
        # Create new QueryClusterNode
        freq_score = 0.1
        recency = 1.0
        success_rate = 1.0 if success else 0.0
        importance = round(0.4 * freq_score + 0.3 * success_rate + 0.3 * recency, 4)
        
        ent_dist = {ent: 1.0 for ent in ents}
        total_weight = sum(ent_dist.values())
        if total_weight > 0:
            ent_dist = {k: round(v / total_weight, 4) for k, v in ent_dist.items()}
            
        new_cluster = QueryClusterNode(
            cluster_id=f"cluster_{uuid.uuid4().hex[:8]}",
            cluster_center_query=query,
            queries=[query],
            entities=ents,
            frequency=1,
            importance_score=importance,
            success_rate=success_rate,
            entity_distribution=ent_dist
        )
        clusters.append(new_cluster)

    # 2. Persist updated cluster states
    save_clusters(clusters)
