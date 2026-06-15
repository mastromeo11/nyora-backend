import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.learning.learning_models import CorrectionNode
from app.learning.learning_store import get_corrections, append_correction

def compile_and_store_correction(
    reason: str,
    original_answer: str,
    corrected_answer: str,
    evidence_ids: List[str] = None,
    source_modalities: List[str] = None,
    reflection_ids: List[str] = None,
    replanning_ids: List[str] = None,
    source: str = "correction_engine"
) -> CorrectionNode:
    """
    Compiles a new CorrectionNode or reinforces an existing correction.
    Maintains full provenance details to preserve origin context.
    """
    now_str = datetime.utcnow().isoformat()
    evidence_ids = evidence_ids or []
    source_modalities = source_modalities or []
    reflection_ids = reflection_ids or []
    replanning_ids = replanning_ids or []

    # Check for existing matching correction based on reason and source
    existing_corrections = get_corrections()
    matched_correction: Optional[CorrectionNode] = None
    
    for corr in existing_corrections:
        if corr.reason.strip().lower() == reason.strip().lower() and corr.source == source:
            matched_correction = corr
            break

    if matched_correction:
        # Reinforce existing correction
        updated_node = CorrectionNode(
            correction_id=matched_correction.correction_id,
            reason=matched_correction.reason,
            reflection_ids=list(set(matched_correction.reflection_ids + reflection_ids)),
            replanning_ids=list(set(matched_correction.replanning_ids + replanning_ids)),
            evidence_ids=list(set(matched_correction.evidence_ids + evidence_ids)),
            source_modalities=list(set(matched_correction.source_modalities + source_modalities)),
            confirmation_count=matched_correction.confirmation_count + 1,
            last_confirmed=now_str,
            original_answer=original_answer or matched_correction.original_answer,
            corrected_answer=corrected_answer or matched_correction.corrected_answer,
            confidence=round(min(matched_correction.confidence + 0.05, 1.0), 4),
            timestamp=matched_correction.timestamp,
            source=matched_correction.source
        )
    else:
        # Create new correction node
        updated_node = CorrectionNode(
            correction_id=f"corr_{uuid.uuid4().hex[:8]}",
            reason=reason,
            reflection_ids=reflection_ids,
            replanning_ids=replanning_ids,
            evidence_ids=evidence_ids,
            source_modalities=source_modalities,
            confirmation_count=1,
            last_confirmed=now_str,
            original_answer=original_answer,
            corrected_answer=corrected_answer,
            confidence=0.70,  # initial confidence
            timestamp=now_str,
            source=source
        )

    append_correction(updated_node)
    return updated_node
