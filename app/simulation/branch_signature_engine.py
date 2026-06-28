import hashlib
from typing import List, Dict, Any

def generate_branch_signature(
    initial_state_id: str,
    modified_variables: Dict[str, Any],
    entities: List[str],
    policy_id: str
) -> str:
    """
    Computes a deterministic hash signature for a branching scenario path.
    """
    # Sort modified variables by key
    mv_str = ",".join(f"{k}:{v}" for k, v in sorted(modified_variables.items()))
    # Sort entities
    sorted_ents = ",".join(sorted(entities))
    
    components = [initial_state_id, mv_str, sorted_ents, policy_id]
    payload = "|".join(components)
    
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
