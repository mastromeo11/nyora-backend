import hashlib

def generate_recommendation_signature(
    item: str,
    category: str,
    action: str
) -> str:
    """
    Generates a deterministic SHA256 signature hash of a recommendation item, category, and action.
    """
    norm_item = (item or "").strip().lower()
    norm_cat = (category or "").strip().lower()
    norm_act = (action or "").strip().lower()
    raw_str = f"{norm_item}:{norm_cat}:{norm_act}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
