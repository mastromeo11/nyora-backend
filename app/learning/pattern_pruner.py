from app.learning.learning_store import load_learning_store, save_learning_store
from app.config import ENABLE_PATTERN_PRUNER

def prune_learning_memory(threshold: float = 0.1) -> dict:
    """
    Purges learning structures (patterns, corrections, failures, clusters)
    whose confidence scores or weights have decayed below the pruning threshold.
    """
    if not ENABLE_PATTERN_PRUNER:
        return {
            "initial_total": 0,
            "pruned_total": 0,
            "pruning_efficiency": 0.0
        }

    mem = load_learning_store()
    
    patterns = mem.setdefault("patterns", {})
    corrections = mem.setdefault("corrections", {})
    failures = mem.setdefault("failure_patterns", {})
    clusters = mem.setdefault("clusters", {})
    feedback = mem.setdefault("feedback", {})

    initial_total = len(patterns) + len(corrections) + len(failures) + len(clusters)

    # 1. Prune Patterns
    pruned_patterns = 0
    for pat_id, pat in list(patterns.items()):
        if pat.get("confidence", 1.0) < threshold:
            del patterns[pat_id]
            pruned_patterns += 1

    # 2. Prune Corrections
    pruned_corrections = 0
    for corr_id, corr in list(corrections.items()):
        if corr.get("confidence", 1.0) < threshold:
            del corrections[corr_id]
            pruned_corrections += 1

    # 3. Prune Failure Patterns
    pruned_failures = 0
    for fail_id, fail in list(failures.items()):
        if fail.get("confidence", 1.0) < threshold:
            del failures[fail_id]
            pruned_failures += 1

    # 4. Prune Clusters
    pruned_clusters = 0
    for clust_id, clust in list(clusters.items()):
        if clust.get("importance_score", 1.0) < threshold or not clust.get("queries"):
            del clusters[clust_id]
            pruned_clusters += 1

    pruned_total = pruned_patterns + pruned_corrections + pruned_failures + pruned_clusters
    pruning_efficiency = (pruned_total / initial_total) if initial_total > 0 else 1.0

    print(f"[LEARNING PRUNER] Pruned: patterns={pruned_patterns}, corrections={pruned_corrections}, failures={pruned_failures}, clusters={pruned_clusters}.")
    
    if pruned_total > 0:
        save_learning_store()
        
    return {
        "initial_total": initial_total,
        "pruned_patterns": pruned_patterns,
        "pruned_corrections": pruned_corrections,
        "pruned_failures": pruned_failures,
        "pruned_clusters": pruned_clusters,
        "pruned_total": pruned_total,
        "pruning_efficiency": pruning_efficiency
    }
