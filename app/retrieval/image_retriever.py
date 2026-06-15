import os
from app.embedding.clip_embedder import embed_text_query
from app.database import db
from app.config import CLIP_MIN_SCORE, VISUAL_WEIGHT, CATEGORY_BOOST_WEIGHT

def detect_query_category(query: str) -> str | None:
    """
    Analyzes the query text for keywords related to the 9 visual categories.
    """
    q = query.lower()
    if "flowchart" in q or "flow-chart" in q:
        return "flowchart"
    if "architecture" in q or "diagram" in q:
        return "architecture diagram"
    if "dashboard" in q:
        return "dashboard"
    if "graph" in q:
        return "graph"
    if "chart" in q or "pie" in q or "bar" in q:
        return "chart"
    if "screenshot" in q or "screen shot" in q:
        return "screenshot"
    if "document" in q or "text" in q or "page" in q:
        return "document"
    if "table" in q or "csv" in q:
        return "table"
    if "ui" in q or "user interface" in q or "screen" in q or "view" in q:
        return "ui screen"
    return None

def get_confidence_label(score: float) -> str:
    """
    Maps numerical similarity scores to qualitative confidence levels.
    """
    if score >= 0.40:
        return "High"
    elif score >= 0.30:
        return "Medium"
    elif score >= 0.20:
        return "Low"
    else:
        return "Very Low"

def retrieve_images(query: str, limit: int = 5, min_score: float = None) -> list[dict]:
    """
    Retrieves images visually matching the search query using CLIP embeddings,
    filtering blank images, applying category-aware boosting, and threshold filtering.
    
    Args:
        query (str): The text query describing the target image.
        limit (int): The maximum number of images to return.
        min_score (float): Optional threshold to override CLIP_MIN_SCORE.
        
    Returns:
        list[dict]: A list of matched, ranked, and deduplicated image results.
    """
    try:
        # 1. Generate CLIP text embedding
        query_embedding = embed_text_query(query)
        
        # 2. Detect query visual category intent
        matched_category = detect_query_category(query)
        
        # We query a slightly larger sample from database to allow room for thresholding and deduplication
        db_limit = max(limit * 3, 15)
        results = db.search_images(query_embedding=query_embedding, n_results=db_limit)
        
        if not results or not results.get("ids") or len(results["ids"][0]) == 0:
            return []
            
        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        
        candidates = []
        for idx in range(len(ids)):
            metadata = metadatas[idx] if metadatas[idx] else {}
            
            # Exclude blank images
            if metadata.get("is_blank") is True:
                continue
                
            # Cosine similarity = 1.0 - distance
            clip_similarity = 1.0 - distances[idx]
            
            # 3. Hybrid scoring & Category Boosting
            if matched_category:
                img_category = metadata.get("visual_category")
                category_match_bonus = 1.0 if img_category == matched_category else 0.0
                final_score = clip_similarity + 0.15 * category_match_bonus
                
                reason = (
                    f"Matched query visual category intent '{matched_category}' "
                    f"({ 'Category match bonus of +0.15 applied' if category_match_bonus > 0 else 'No category match' }). "
                    f"Raw CLIP Similarity: {clip_similarity:.4f}."
                )
            else:
                final_score = clip_similarity
                reason = f"CLIP similarity matched query semantic description. Raw Score: {clip_similarity:.4f}."

                
            # 4. Threshold filtering
            threshold = min_score if min_score is not None else CLIP_MIN_SCORE
            if final_score < threshold:
                continue
                
            confidence = get_confidence_label(final_score)
            
            candidates.append({
                "id": ids[idx],
                "score": final_score,
                "raw_clip_score": clip_similarity,
                "confidence": confidence,
                "retrieved_reason": reason,
                "source": metadata.get("source"),
                "source_type": metadata.get("source_type", "image"),
                "file_path": metadata.get("file_path"),
                "ocr_confidence": metadata.get("ocr_confidence"),
                "visual_category": metadata.get("visual_category", "document"),
                "metadata": metadata
            })
            
        # 5. Sort candidates by final score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # 6. Deduplicate by source filename (keeping highest score per source)
        deduplicated = []
        seen_sources = set()
        for cand in candidates:
            src = cand["source"]
            if src not in seen_sources:
                seen_sources.add(src)
                deduplicated.append(cand)
            if len(deduplicated) >= limit:
                break
                
        return deduplicated
    except Exception as e:
        print(f"Error performing visual search for query '{query}': {e}")
        return []

def retrieve_top_image(query: str) -> dict | None:
    """
    Retrieves the single highest-scoring, non-blank deduplicated visual matching image candidate.
    """
    from app.config import VQA_MIN_SCORE
    results = retrieve_images(query, limit=1, min_score=VQA_MIN_SCORE)
    if results:
        res = results[0]
        return {
            "source": res["source"],
            "file_path": res["file_path"],
            "score": res["score"],
            "visual_category": res["visual_category"],
            "confidence": res["confidence"]
        }
    return None
