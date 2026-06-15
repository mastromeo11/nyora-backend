from typing import List, Dict, Any
from app.config import ENABLE_ACTIVE_LEARNING
from app.learning.correction_engine import compile_and_store_correction
from app.learning.failure_pattern_engine import compile_and_store_failure_pattern

def evaluate_active_learning(
    query: str,
    answer: str,
    confidence_label: str,
    grounding_report: List[Dict[str, Any]],
    executed_tools: List[Any] = None,
    reflections: List[Any] = None
) -> dict:
    """
    Evaluates response quality to trigger active continual learning.
    Recommends corrective steps (forced replans, extra retrieval attempts)
    without fabricating facts.
    """
    if not ENABLE_ACTIVE_LEARNING:
        return {"replan_recommended": False, "extra_retrieval_recommended": False}

    replan_rec = False
    extra_retrieval = False
    
    # 1. Detect grounding refutations
    has_refutations = False
    refuted_claims = []
    if grounding_report:
        for item in grounding_report:
            if str(item.get("status", "")).lower() == "refuted":
                has_refutations = True
                refuted_claims.append(item.get("claim", ""))

    if has_refutations:
        replan_rec = True
        extra_retrieval = True
        # Generate an advisory CorrectionNode
        reason = f"Grounding refutation: {refuted_claims[0][:60]}..." if refuted_claims else "Grounding refutation"
        compile_and_store_correction(
            reason=reason,
            original_answer=answer,
            corrected_answer="Grounding correction applied.",
            source="grounding_validator"
        )

    # 2. Detect repeated tool failures or reflections
    tool_failures = []
    if reflections:
        replan_rec = True
        for refl in reflections:
            r_type = getattr(refl, "failure_type", "execution_error")
            r_reason = getattr(refl, "reason", "reflection error")
            tool_failures.append(r_reason)
            # Generate a FailurePatternNode to catalog the execution crash
            compile_and_store_failure_pattern(
                failure_type=r_type,
                tool_failures=[r_reason],
                is_restart=True
            )

    # 3. Detect low-confidence outputs
    is_low_conf = str(confidence_label).lower() == "low"
    if is_low_conf:
        extra_retrieval = True
        compile_and_store_failure_pattern(
            failure_type="low_confidence_output",
            is_timeout=False
        )

    return {
        "replan_recommended": replan_rec,
        "extra_retrieval_recommended": extra_retrieval,
        "flagged_issues": {
            "has_refutations": has_refutations,
            "reflections_count": len(reflections) if reflections else 0,
            "is_low_confidence": is_low_conf
        }
    }
