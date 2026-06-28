import hashlib

def generate_preference_signature(
    domain: str,
    tone: str,
    length: int,
    depth: str
) -> str:
    """
    Generates a deterministic SHA256 signature hash of preference configurations.
    """
    norm_domain = (domain or "").strip().lower()
    norm_tone = (tone or "").strip().lower()
    norm_depth = (depth or "").strip().lower()
    raw_str = f"{norm_domain}:{norm_tone}:{length}:{norm_depth}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
