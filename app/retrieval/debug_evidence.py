from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.evidence_graph import build_evidence_graph

def format_evidence_graph(evidence_list: list[EvidenceNode]) -> dict:
    """
    Exposes full evidence graph nodes and edges.
    """
    return build_evidence_graph(evidence_list)

def format_ranking_details(evidence_list: list[EvidenceNode]) -> list[dict]:
    """
    Formats dynamic ranking diagnostic logs for inspection.
    """
    debug_list = []
    for idx, node in enumerate(evidence_list):
        debug_list.append({
            "rank": idx + 1,
            "evidence_id": node.evidence_id,
            "source": node.source,
            "modality": node.modality,
            "score": node.retrieval_score,
            "confidence": node.confidence,
            "reason": node.citation_reason,
            "provenance": node.provenance
        })
    return debug_list
