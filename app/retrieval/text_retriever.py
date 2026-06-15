from app.database import db
from app.config import TEXT_MIN_SCORE

def get_text_confidence_label(score: float) -> str:
    """
    Maps numerical text similarity scores to qualitative confidence levels.
    """
    if score >= 0.75:
        return "High"
    elif score >= 0.65:
        return "Medium"
    elif score >= 0.50:
        return "Low"
    else:
        return "Very Low"

def retrieve_text(query_text: str, n_results: int = 5) -> list[dict]:
    """
    Performs semantic similarity search against the persistent ChromaDB text collection,
    applying threshold filtering, confidence mapping, and source deduplication.
    
    Args:
        query_text (str): The search query text.
        n_results (int): The number of matching chunks to retrieve.
        
    Returns:
        list[dict]: A list of filtered and deduplicated retrieved text chunks.
    """
    try:
        # Request a larger pool to allow room for thresholding and deduplication
        db_limit = max(n_results * 3, 15)
        results = db.search_documents(query_texts=[query_text], n_results=db_limit)
        formatted_results = []
        
        if not results or not results.get("ids") or len(results["ids"]) == 0:
            return formatted_results
            
        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        documents = results["documents"][0] if results.get("documents") else [""] * len(ids)
        
        candidates = []
        for idx in range(len(ids)):
            # Cosine similarity score = 1.0 - distance
            score = 1.0 - distances[idx]
            
            # Apply threshold filtering
            if score < TEXT_MIN_SCORE:
                continue
                
            confidence = get_text_confidence_label(score)
            metadata = metadatas[idx] if metadatas[idx] else {}
            
            candidates.append({
                "id": ids[idx],
                "score": score,
                "confidence": confidence,
                "text": documents[idx],
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "source_type": metadata.get("source_type"),
                "timestamp_start": metadata.get("timestamp_start"),
                "timestamp_end": metadata.get("timestamp_end"),
                "ocr_confidence": metadata.get("ocr_confidence"),
                "retrieved_reason": f"Text chunk semantic match (BGE Score: {score:.4f}, Confidence: {confidence})",
                "metadata": metadata
            })
            
        # Sort candidates descending by score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Deduplicate by source filename, keeping the highest score
        deduplicated = []
        seen_sources = set()
        for cand in candidates:
            src = cand["source"]
            if src not in seen_sources:
                seen_sources.add(src)
                deduplicated.append(cand)
            if len(deduplicated) >= n_results:
                break
                
        return deduplicated
    except Exception as e:
        print(f"Error performing semantic retrieval for query '{query_text}': {e}")
        return []
