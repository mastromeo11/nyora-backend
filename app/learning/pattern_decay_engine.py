from app.config import (
    ENABLE_PATTERN_DECAY,
    PATTERN_DECAY_FACTOR,
    CORRECTION_DECAY_FACTOR,
    FAILURE_PATTERN_DECAY_FACTOR
)
from app.learning.learning_store import load_learning_store, save_learning_store

def decay_learning_memory():
    """
    Applies temporal decay factor reductions to patterns, corrections,
    and failure logs to prevent static historical memory dominance.
    """
    if not ENABLE_PATTERN_DECAY:
        print("[LEARNING DECAY] Learning decay is disabled in config.")
        return

    mem = load_learning_store()
    
    patterns = mem.setdefault("patterns", {})
    corrections = mem.setdefault("corrections", {})
    failures = mem.setdefault("failure_patterns", {})

    # 1. Decay Pattern confidence
    for pat_id, pat in patterns.items():
        old_conf = pat.get("confidence", 1.0)
        old_imp = pat.get("importance_score", 0.0)
        pat["confidence"] = round(old_conf * PATTERN_DECAY_FACTOR, 4)
        pat["importance_score"] = round(old_imp * PATTERN_DECAY_FACTOR, 4)

    # 2. Decay Correction confidence
    for corr_id, corr in corrections.items():
        old_conf = corr.get("confidence", 1.0)
        corr["confidence"] = round(old_conf * CORRECTION_DECAY_FACTOR, 4)

    # 3. Decay Failure Pattern confidence
    for fail_id, fail in failures.items():
        old_conf = fail.get("confidence", 1.0)
        fail["confidence"] = round(old_conf * FAILURE_PATTERN_DECAY_FACTOR, 4)

    print(f"[LEARNING DECAY] Decayed {len(patterns)} patterns, {len(corrections)} corrections, and {len(failures)} failure patterns.")
    save_learning_store()
