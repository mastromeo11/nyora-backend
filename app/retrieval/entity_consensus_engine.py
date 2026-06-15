import re
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.evidence_graph import get_node_entities

class EntityConsensusNode:
    def __init__(self, entity: str, modalities: list[str], snippets: list[str], consensus_score: float):
        self.entity = entity
        self.modalities = modalities
        self.snippets = snippets
        self.consensus_score = consensus_score

    def dict(self) -> dict:
        return {
            "entity": self.entity,
            "modalities": self.modalities,
            "snippets": self.snippets,
            "consensus_score": self.consensus_score
        }

def calculate_modality_bonus(modalities_count: int) -> float:
    """
    Computes cross-modal consensus boost:
    1 modality  -> +0.00
    2 modalities -> +0.05
    3 modalities -> +0.10
    4 modalities -> +0.15
    5+ modalities -> +0.20
    """
    if modalities_count <= 1:
        return 0.0
    return min(0.05 * (modalities_count - 1), 0.20)

def aggregate_entity_consensus(evidence_nodes: list[EvidenceNode]) -> list[EntityConsensusNode]:
    """
    Aggregates evidence nodes around distinct entities.
    Returns a list of EntityConsensusNode objects.
    """
    entity_map = {}
    
    for node in evidence_nodes:
        # Extract matching entities from node content and source (handling phonetic variants)
        entities = get_node_entities(node.content).union(get_node_entities(node.source))
        
        for ent in entities:
            # Standardize key (matching key entity name)
            ent_key = ent.lower()
            if ent_key not in entity_map:
                entity_map[ent_key] = {}
                
            modality = node.modality.lower()
            if modality not in entity_map[ent_key]:
                entity_map[ent_key][modality] = []
                
            # Avoid duplicate identical snippets under the same modality
            if node.content not in entity_map[ent_key][modality]:
                entity_map[ent_key][modality].append(node.content)
                
    consensus_nodes = []
    for ent, modality_snippets in entity_map.items():
        modalities = sorted(list(modality_snippets.keys()))
        snippets = []
        for mod in modalities:
            snippets.extend(modality_snippets[mod])
            
        score = calculate_modality_bonus(len(modalities))
        
        consensus_nodes.append(EntityConsensusNode(
            entity=ent,
            modalities=modalities,
            snippets=snippets,
            consensus_score=round(score, 4)
        ))
        
    return consensus_nodes
