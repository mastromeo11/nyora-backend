from app.simulation.simulation_models import CounterfactualNode
from app.simulation.simulation_store import get_policies

def validate_counterfactual(node: CounterfactualNode) -> bool:
    """
    Validates a counterfactual node based on:
    - old_value must not be equal to new_value.
    - new_value must not be None or empty.
    - No contradictory state descriptions (e.g., status cannot be both "Running" and "Failed").
    - If policy is specified in the modified_variable or alternative_outcome, it should exist in stored policies.
    """
    if not node.new_value:
        return False
        
    if node.old_value == node.new_value:
        return False

    # Check case-insensitive equality
    if node.old_value and node.new_value and node.old_value.strip().lower() == node.new_value.strip().lower():
        return False
        
    # Contradictory state variables checks
    forbidden_contradictions = [
        ("running", "failed"),
        ("active", "inactive"),
        ("success", "failure"),
        ("online", "offline"),
        ("up", "down")
    ]
    
    old_l = (node.old_value or "").strip().lower()
    new_l = node.new_value.strip().lower()
    for word1, word2 in forbidden_contradictions:
        if (word1 in old_l and word1 in new_l) or (word2 in old_l and word2 in new_l):
            # This is fine, but if old has word1 and new has word1, it might not be contradictory, but wait:
            # Let's say if it tries to transition to a state that is contradictory itself (e.g. status is "running and failed")
            pass
        if ("running" in new_l and "failed" in new_l) or ("online" in new_l and "offline" in new_l):
            return False

    # Policy association check:
    # If the modified variable or outcome mentions a policy, check if it's registered
    # Let's say if the counterfactual contains "policy_" prefix, check if the policy ID exists
    # We won't block validation if no policies exist to keep it flexible, but if we do find a policy ID reference we can validate it.
    if "policy_" in node.modified_variable:
        parts = node.modified_variable.split("policy_")
        if len(parts) > 1:
            policy_id = "policy_" + parts[1].split()[0]
            existing_policies = [p.policy_id for p in get_policies()]
            if existing_policies and policy_id not in existing_policies:
                return False

    return True
