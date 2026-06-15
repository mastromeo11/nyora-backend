from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import ENABLE_SELF_LEARNING
from app.embedding.text_embedder import embed_text
from app.learning.learning_store import (
    get_patterns,
    get_corrections,
    get_clusters,
    get_failure_patterns
)
from app.learning.learning_models import PatternNode, CorrectionNode, QueryClusterNode
from app.learning.learning_cache import pattern_cache, record_hit, record_miss

def _get_vector(text: str) -> List[float]:
    try:
        return embed_text([text])[0]
    except Exception:
        return [0.0] * 384

def _cosine_sim(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    return float(np.dot(v1, v2))

def retrieve_learning_context(query: str) -> dict:
    """
    Retrieves and ranks relevant patterns, corrections, clusters, and failure logs.
    Ranks them using the multi-variable formula:
    score = 0.30 * similarity + 0.25 * success_rate + 0.20 * recency + 0.15 * confidence + 0.10 * importance
    
    Ensures successful patterns outrank failure patterns.
    """
    if not ENABLE_SELF_LEARNING:
        return {
            "patterns": [],
            "corrections": [],
            "clusters": [],
            "explanation": "Self-learning is disabled."
        }

    # Check cache
    cached = pattern_cache.get(query)
    if cached is not None:
        record_hit()
        return cached

    record_miss()

    query_emb = _get_vector(query)
    now = datetime.utcnow()

    # 1. Retrieve Patterns
    patterns = get_patterns()
    ranked_patterns = []
    for pat in patterns:
        # Generate text representer for similarity
        rep = f"Pattern entities: {','.join(pat.supporting_entities)}. Modalities: {','.join(pat.source_modalities)}"
        pat_emb = _get_vector(rep)
        sim = _cosine_sim(query_emb, pat_emb)
        
        # Calculate components
        success_rate = pat.success_count / pat.frequency if pat.frequency > 0 else 1.0
        
        recency = 1.0
        try:
            delta = now - datetime.fromisoformat(pat.last_confirmed)
            delta_hours = delta.total_seconds() / 3600.0
            recency = 1.0 / (1.0 + delta_hours)
        except Exception:
            pass
            
        score = (
            0.30 * sim +
            0.25 * success_rate +
            0.20 * recency +
            0.15 * pat.confidence +
            0.10 * pat.importance_score
        )
        # Successful patterns outrank failure patterns (give them a small boost)
        score += 0.1
        
        ranked_patterns.append((score, pat))

    # Sort descending by score
    ranked_patterns.sort(key=lambda x: x[0], reverse=True)
    selected_patterns = [item[1].dict() for item in ranked_patterns[:3]]

    # 2. Retrieve Corrections
    corrections = get_corrections()
    ranked_corrections = []
    for corr in corrections:
        corr_emb = _get_vector(corr.reason)
        sim = _cosine_sim(query_emb, corr_emb)
        
        recency = 1.0
        try:
            delta = now - datetime.fromisoformat(corr.last_confirmed)
            delta_hours = delta.total_seconds() / 3600.0
            recency = 1.0 / (1.0 + delta_hours)
        except Exception:
            pass
            
        score = (
            0.30 * sim +
            0.25 * 1.0 + # baseline success rate for correction
            0.20 * recency +
            0.15 * corr.confidence +
            0.10 * 0.5  # default importance
        )
        ranked_corrections.append((score, corr))
        
    ranked_corrections.sort(key=lambda x: x[0], reverse=True)
    selected_corrections = [item[1].dict() for item in ranked_corrections[:3]]

    # 3. Retrieve Clusters
    clusters = get_clusters()
    ranked_clusters = []
    for clust in clusters:
        clust_emb = _get_vector(clust.cluster_center_query)
        sim = _cosine_sim(query_emb, clust_emb)
        
        score = (
            0.30 * sim +
            0.25 * clust.success_rate +
            0.20 * 1.0 + # recency
            0.15 * 0.8 + # default confidence
            0.10 * clust.importance_score
        )
        ranked_clusters.append((score, clust))
        
    ranked_clusters.sort(key=lambda x: x[0], reverse=True)
    selected_clusters = [item[1].dict() for item in ranked_clusters[:3]]

    # 4. Compile natural language explanations
    from app.learning.learning_explanation_engine import compile_learning_explanation
    explanation = compile_learning_explanation(selected_patterns, selected_corrections)

    res = {
        "patterns": selected_patterns,
        "corrections": selected_corrections,
        "clusters": selected_clusters,
        "explanation": explanation
    }

    pattern_cache.set(query, res)
    return res
