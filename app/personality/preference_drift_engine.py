from app.embedding.text_embedder import embed_text

def detect_preference_drift(old_text: str, recent_text: str, threshold: float = 0.4) -> bool:
    """
    Computes drift_score = 1.0 - cosine(old_preference, recent_preference).
    Returns True if the drift score exceeds the threshold, signifying a major habit shift.
    """
    if not old_text or not recent_text:
        return False
        
    try:
        embs = embed_text([old_text, recent_text])
        old_emb = embs[0]
        recent_emb = embs[1]
        
        dot_prod = sum(a * b for a, b in zip(old_emb, recent_emb))
        mag_old = sum(a * a for a in old_emb) ** 0.5
        mag_recent = sum(b * b for b in recent_emb) ** 0.5
        
        cosine_sim = dot_prod / (mag_old * mag_recent + 1e-9)
        drift_score = 1.0 - cosine_sim
        return drift_score > threshold
    except Exception as e:
        print(f"[PREFERENCE DRIFT] Embedding computation fallback: {e}")
        # Word overlap fallback
        old_words = set(old_text.lower().split())
        recent_words = set(recent_text.lower().split())
        if not old_words or not recent_words:
            return False
        overlap = len(old_words & recent_words) / max(len(old_words), len(recent_words))
        drift_score = 1.0 - overlap
        return drift_score > threshold
