import hashlib
from typing import List

def generate_strategy_signature(intent: str, planner_type: str, tool_sequence: List[str], entities: List[str]) -> str:
    """
    Generates a deterministic SHA256 hash representation of a strategy signature
    based on query intent, planner type, tool sequence, and entities.
    """
    sorted_tools = ",".join(sorted(tool_sequence or []))
    sorted_ents = ",".join(sorted(entities or []))
    raw_str = f"{intent or ''}:{planner_type or ''}:{sorted_tools}:{sorted_ents}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
