import hashlib
from typing import List

def generate_policy_signature(planner_type: str, tool_sequence: List[str], intent_type: str, entities: List[str]) -> str:
    """
    Generates a deterministic SHA256 hash representation of a policy signature
    based on planner type, tool sequence, intent, and entities.
    """
    sorted_tools = ",".join(sorted(tool_sequence or []))
    sorted_ents = ",".join(sorted(entities or []))
    raw_str = f"{planner_type or ''}:{sorted_tools}:{intent_type or ''}:{sorted_ents}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
