import uuid
from datetime import datetime
from typing import List, Optional
from app.episodic.episodic_models import FailureReplayNode
from app.episodic.episodic_store import get_failure_replays, append_failure_replay

def record_failure_replay(
    failure_type: str, 
    tool_failures: List[str], 
    agent_failures: List[str], 
    is_timeout: bool
) -> FailureReplayNode:
    """
    Stores and reinforcements failed experience patterns separately.
    """
    all_failures = get_failure_replays()
    now_str = datetime.utcnow().isoformat()
    
    existing_fail: Optional[FailureReplayNode] = None
    for f in all_failures:
        if f.failure_type == failure_type:
            existing_fail = f
            break
            
    if existing_fail:
        existing_fail.frequency += 1
        existing_fail.last_seen = now_str
        if is_timeout:
            existing_fail.timeout_events += 1
            
        # Merge lists without duplicates
        existing_fail.tool_failures = list(set(existing_fail.tool_failures + tool_failures))
        existing_fail.agent_failures = list(set(existing_fail.agent_failures + agent_failures))
        
        append_failure_replay(existing_fail)
        print(f"[FAILURE REPLAY] Reinforced failure signature: {failure_type} (frequency: {existing_fail.frequency}).")
        return existing_fail
    else:
        failure_replay_id = f"fail_rep_{uuid.uuid4().hex[:8]}"
        new_fail = FailureReplayNode(
            failure_replay_id=failure_replay_id,
            failure_type=failure_type,
            tool_failures=tool_failures,
            agent_failures=agent_failures,
            timeout_events=1 if is_timeout else 0,
            frequency=1,
            last_seen=now_str
        )
        append_failure_replay(new_fail)
        print(f"[FAILURE REPLAY] Logged new failure pattern: {failure_type}.")
        return new_fail
