import uuid
from datetime import datetime
from app.database import db
from app.retrieval.image_retriever import retrieve_images
from app.llm.vision_client import ask_image_question
from app.retrieval.evidence_models import EvidenceNode
from app.config import MAX_VQA_CANDIDATES

def map_db_results_to_nodes(results: dict, modality_type: str, retriever_name: str) -> list[EvidenceNode]:
    nodes = []
    if not results or not results.get("ids") or len(results["ids"]) == 0:
        return nodes
        
    ids = results["ids"][0]
    distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
    metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
    documents = results["documents"][0] if results.get("documents") else [""] * len(ids)
    
    for idx in range(len(ids)):
        score = 1.0 - distances[idx]
        metadata = metadatas[idx] or {}
        
        # Simple confidence calculation based on raw score
        if score >= 0.75:
            confidence = "High"
        elif score >= 0.50:
            confidence = "Medium"
        else:
            confidence = "Low"
            
        timestamp_start = metadata.get("timestamp_start")
        if timestamp_start is not None:
            timestamp_start = float(timestamp_start)
            
        timestamp_end = metadata.get("timestamp_end")
        if timestamp_end is not None:
            timestamp_end = float(timestamp_end)
            
        source = metadata.get("source", "unknown")
        source_type = metadata.get("source_type", modality_type)
        
        nodes.append(EvidenceNode(
            evidence_id=f"node_{modality_type}_{uuid.uuid4().hex[:8]}",
            source=source,
            source_type=source_type,
            modality=modality_type,
            content=documents[idx],
            retrieval_score=score,
            confidence=confidence,
            citation_reason=f"Matched {modality_type} context from {source}",
            metadata=metadata,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            visual_category=metadata.get("visual_category"),
            file_path=metadata.get("file_path"),
            provenance={
                "retriever": retriever_name,
                "retrieval_timestamp": datetime.utcnow().isoformat(),
                "ranking_stage": "retrieved",
                "fusion_stage": "raw"
            }
        ))
    return nodes

def retrieve_evidence(query: str, limit: int = 5) -> list[EvidenceNode]:
    evidence_list = []
    
    # 1. Fetch Text evidence (PDF/DOCX)
    try:
        res_text = db.text_collection.query(
            query_texts=[query],
            n_results=limit * 2,
            where={"source_type": {"$in": ["pdf", "docx"]}}
        )
        evidence_list.extend(map_db_results_to_nodes(res_text, "text", "bge-small-en-v1.5"))
    except Exception as e:
        print(f"Error retrieving text evidence: {e}")
        
    # 2. Fetch OCR evidence
    try:
        res_ocr = db.text_collection.query(
            query_texts=[query],
            n_results=limit * 2,
            where={"source_type": "image"}
        )
        evidence_list.extend(map_db_results_to_nodes(res_ocr, "ocr", "bge-small-en-v1.5"))
    except Exception as e:
        print(f"Error retrieving OCR evidence: {e}")
        
    # 3. Fetch Audio evidence
    try:
        res_audio = db.text_collection.query(
            query_texts=[query],
            n_results=limit * 2,
            where={"source_type": "audio"}
        )
        evidence_list.extend(map_db_results_to_nodes(res_audio, "audio", "bge-small-en-v1.5"))
    except Exception as e:
        print(f"Error retrieving audio evidence: {e}")
        
    # 4. Fetch Image matches (CLIP)
    try:
        images = retrieve_images(query, limit=limit * 2)
        for img in images:
            metadata = img.get("metadata") or {}
            evidence_list.append(EvidenceNode(
                evidence_id=f"node_image_{uuid.uuid4().hex[:8]}",
                source=img["source"],
                source_type="image",
                modality="image",
                content=f"Image file {img['source']}.",
                retrieval_score=img["score"],
                confidence=img["confidence"],
                citation_reason=img.get("retrieved_reason", "Matched visual search"),
                metadata=metadata,
                visual_category=img.get("visual_category"),
                file_path=img.get("file_path"),
                provenance={
                    "retriever": "clip-vit-base-patch32",
                    "retrieval_timestamp": datetime.utcnow().isoformat(),
                    "ranking_stage": "retrieved",
                    "fusion_stage": "raw"
                }
            ))
            
            # 5. Fetch Cached Captions as separate nodes
            caption = metadata.get("caption")
            if caption:
                evidence_list.append(EvidenceNode(
                    evidence_id=f"node_caption_{uuid.uuid4().hex[:8]}",
                    source=img["source"],
                    source_type="image",
                    modality="caption",
                    content=caption,
                    retrieval_score=img["score"],
                    confidence=img["confidence"],
                    citation_reason=f"Cached caption for visual document {img['source']}",
                    metadata=metadata,
                    visual_category=img.get("visual_category"),
                    file_path=img.get("file_path"),
                    provenance={
                        "retriever": "llava:7b",
                        "retrieval_timestamp": datetime.utcnow().isoformat(),
                        "ranking_stage": "retrieved",
                        "fusion_stage": "raw"
                    }
                ))
    except Exception as e:
        print(f"Error retrieving image and caption evidence: {e}")
        
    # 6. Fetch Visual Question Answering (VQA) answers
    try:
        # Run visual QA on top matching candidates
        vqa_candidates = retrieve_images(query, limit=MAX_VQA_CANDIDATES)
        for img in vqa_candidates:
            image_path = img.get("file_path")
            source = img.get("source")
            score = img.get("score")
            
            ans = ask_image_question(image_path, query)
            
            if ans and ans != "The information is not visible in the image.":
                evidence_list.append(EvidenceNode(
                    evidence_id=f"node_vqa_{uuid.uuid4().hex[:8]}",
                    source=source,
                    source_type="image",
                    modality="vqa",
                    content=ans,
                    retrieval_score=score,
                    confidence=img["confidence"],
                    citation_reason=f"Visual question answer generated from diagram {source}",
                    metadata=img.get("metadata"),
                    visual_category=img.get("visual_category"),
                    file_path=image_path,
                    provenance={
                        "retriever": "llava:7b",
                        "retrieval_timestamp": datetime.utcnow().isoformat(),
                        "ranking_stage": "retrieved",
                        "fusion_stage": "raw"
                    }
                ))
    except Exception as e:
        print(f"Error retrieving VQA evidence: {e}")
        
    # Deduplicate elements by (source, content)
    deduped = {}
    for node in evidence_list:
        key = (node.source, node.content)
        if key not in deduped or node.retrieval_score > deduped[key].retrieval_score:
            deduped[key] = node
            
    return list(deduped.values())
