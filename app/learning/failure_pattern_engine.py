import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.learning.learning_models import FailurePatternNode
from app.learning.learning_store import get_failure_patterns, append_failure_pattern
from app.config import ENABLE_FAILURE_PATTERN_TRACKING

def compile_and_store_failure_pattern(
    failure_type: str,
    tool_failures: List[str] = None,
    grounding_failures: List[str] = None,
    is_timeout: bool = False,
    is_restart: bool = False
) -> Optional[FailurePatternNode]:
    """
    Extracts and compiles failure patterns independently from successful plan execution traces.
    """
    if not ENABLE_FAILURE_PATTERN_TRACKING:
        return None

    now_str = datetime.utcnow().isoformat()
    tool_failures = tool_failures or []
    grounding_failures = grounding_failures or []

    # Check for existing failure pattern node
    existing_failures = get_failure_patterns()
    matched_failure: Optional[FailurePatternNode] = None
    for f in existing_failures:
        if f.failure_type.strip().lower() == failure_type.strip().lower():
            matched_failure = f
            break

    if matched_failure:
        # Reinforce failure node statistics
        t_count = matched_failure.timeout_count + (1 if is_timeout else 0)
        r_count = matched_failure.restart_count + (1 if is_restart else 0)
        
        updated_node = FailurePatternNode(
            failure_pattern_id=matched_failure.failure_pattern_id,
            failure_type=matched_failure.failure_type,
            tool_failures=list(set(matched_failure.tool_failures + tool_failures)),
            grounding_failures=list(set(matched_failure.grounding_failures + grounding_failures)),
            timeout_count=t_count,
            restart_count=r_count,
            confidence=round(min(matched_failure.confidence + 0.05, 1.0), 4),
            last_seen=now_str,
            created_at=matched_failure.created_at
        )
    else:
        # Create new failure pattern node
        updated_node = FailurePatternNode(
            failure_pattern_id=f"fail_{uuid.uuid4().hex[:8]}",
            failure_type=failure_type,
            tool_failures=tool_failures,
            grounding_failures=grounding_failures,
            timeout_count=1 if is_timeout else 0,
            restart_count=1 if is_restart else 0,
            confidence=0.60,
            last_seen=now_str,
            created_at=now_str
        )

    append_failure_pattern(updated_node)
    return updated_node
