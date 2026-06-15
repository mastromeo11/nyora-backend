import uuid
from datetime import datetime
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.context_builder import get_node_entities

def compress_evidence(evidence_list: list[EvidenceNode]) -> list[EvidenceNode]:
    """
    Compresses evidence list by entity and source.
    - Merges image nodes (OCR + Caption + VQA) from the same source image sharing the same entity.
    - Deduplicates identical or subset text/audio nodes for the same entity and source.
    - Sorts final results by score descending.
    """
    image_groups = {}  # (source, entity) -> list of nodes
    text_audio_nodes = []
    
    for node in evidence_list:
        is_image = node.source and (
            node.source.lower().endswith(".png") or 
            node.source.lower().endswith(".jpg") or 
            node.source.lower().endswith(".jpeg")
        )
        
        if is_image:
            node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
            if not node_ents:
                node_ents = {"general_visual"}
                
            for ent in node_ents:
                key = (node.source, ent)
                image_groups.setdefault(key, []).append(node)
        else:
            text_audio_nodes.append(node)
            
    compressed_list = []
    
    # 1. Merge image-based nodes per (source, entity)
    for (source, ent), nodes in image_groups.items():
        if len(nodes) == 1:
            compressed_list.append(nodes[0])
            continue
            
        vqa_parts = []
        caption_parts = []
        ocr_parts = []
        
        highest_score = 0.0
        best_confidence = "Low"
        best_node = None
        modalities = set()
        
        for n in nodes:
            if n.retrieval_score > highest_score:
                highest_score = n.retrieval_score
                best_confidence = n.confidence
                best_node = n
            
            mod = n.modality.lower()
            modalities.add(mod)
            
            if mod == "vqa" and n.content not in vqa_parts:
                vqa_parts.append(n.content)
            elif mod == "caption" and n.content not in caption_parts:
                caption_parts.append(n.content)
            elif mod == "ocr" and n.content not in ocr_parts:
                ocr_parts.append(n.content)
                
        # Format the combined content string
        merged_parts = []
        if caption_parts:
            merged_parts.append(f"Caption: {caption_parts[0]}")
        if ocr_parts:
            clean_ocr = " ".join([line.strip() for line in ocr_parts[0].split("\n") if line.strip()])
            merged_parts.append(f"OCR: {clean_ocr}")
        if vqa_parts:
            merged_parts.append(f"VQA: {vqa_parts[0]}")
            
        combined_content = " | ".join(merged_parts)
        if not combined_content:
            combined_content = f"Visual reference match for image {source}"
            
        merged_node = EvidenceNode(
            evidence_id=f"node_merged_img_{uuid.uuid4().hex[:8]}",
            source=source,
            source_type="image",
            modality=best_node.modality if best_node else "image",
            content=combined_content,
            retrieval_score=highest_score,
            confidence=best_confidence,
            citation_reason=best_node.citation_reason if best_node else f"Merged visual evidence for {source}",
            metadata={
                **(best_node.metadata if best_node and best_node.metadata else {}),
                "merged_modalities": sorted(list(modalities)),
                "entity": ent
            },
            visual_category=best_node.visual_category if best_node else None,
            file_path=best_node.file_path if best_node else None,
            provenance={
                "retriever": "evidence_compressor",
                "retrieval_timestamp": datetime.utcnow().isoformat(),
                "ranking_stage": "compressed",
                "fusion_stage": "merged_by_entity"
            }
        )
        compressed_list.append(merged_node)
        
    # 2. Merge highly similar text/audio chunks (overlap containment)
    doc_nodes = {}
    for node in text_audio_nodes:
        is_redundant = False
        node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
        
        for existing_id, existing in list(doc_nodes.items()):
            if existing.source == node.source:
                existing_ents = get_node_entities(existing.content).union(get_node_entities(existing.source))
                # Check subset under same entity match
                if node_ents.intersection(existing_ents):
                    if node.content in existing.content:
                        is_redundant = True
                        break
                    elif existing.content in node.content:
                        del doc_nodes[existing_id]
                        break
                        
        if not is_redundant:
            doc_nodes[node.evidence_id] = node
            
    compressed_list.extend(doc_nodes.values())
    
    # Sort globally by score descending
    compressed_list.sort(key=lambda x: x.retrieval_score, reverse=True)
    return compressed_list
