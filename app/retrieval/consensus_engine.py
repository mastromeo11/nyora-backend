from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.evidence_graph import get_node_entities

def evaluate_consensus(evidence_list: list[EvidenceNode]) -> tuple[float, list[str]]:
    """
    Evaluates semantic consensus across modalities.
    Checks which distinct modalities (e.g. text, ocr, audio, vqa) mention the same entities.
    
    Returns:
        tuple[float, list[str]]: (consensus_score, supporting_modalities)
    """
    if not evidence_list:
        return 0.0, []
        
    entity_modalities = {}
    
    for node in evidence_list:
        node_entities = get_node_entities(node.content).union(get_node_entities(node.source))
        for ent in node_entities:
            entity_modalities.setdefault(ent, set()).add(node.modality.lower())
            
    # Find the entity with the highest cross-modal consensus
    top_entity = None
    max_modalities = 0
    supporting_modalities = []
    
    for ent, modalities in entity_modalities.items():
        if len(modalities) > max_modalities:
            max_modalities = len(modalities)
            top_entity = ent
            supporting_modalities = sorted(list(modalities))
            
    # Calculate consensus boost:
    # 1 modality  -> +0.00
    # 2 modalities -> +0.05
    # 3 modalities -> +0.10
    # 4 modalities -> +0.15
    # 5+ modalities -> +0.20
    if max_modalities > 1:
        consensus_score = min(0.05 * (max_modalities - 1), 0.20)
    else:
        consensus_score = 0.0
        supporting_modalities = []
        if evidence_list:
            supporting_modalities = sorted(list(set(node.modality.lower() for node in evidence_list)))
            
    return round(consensus_score, 4), supporting_modalities

