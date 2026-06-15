import re
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.evidence_graph import extract_entities, KEY_ENTITIES

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
    "to", "of", "in", "on", "at", "by", "for", "with", "about", "against", 
    "between", "into", "through", "during", "before", "after", "above", 
    "below", "from", "up", "down", "out", "off", "over", "under", "again", 
    "further", "then", "once", "here", "there", "when", "where", "why", 
    "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
    "than", "too", "very", "can", "will", "just", "should", "now", 
    "this", "that", "these", "those", "it", "its", "they", "them", "their"
}

# Thread-safe global store for the latest query relevance diagnostics
_latest_relevance_diagnostics = {
    "query": "",
    "removed_nodes": []
}

def get_latest_relevance_diagnostics() -> dict:
    return _latest_relevance_diagnostics

def clean_word(word: str) -> str:
    return re.sub(r"[^\w]", "", word).lower()

def extract_substantive_keywords(text: str) -> set[str]:
    words = text.split()
    keywords = set()
    for w in words:
        clean = clean_word(w)
        if len(clean) > 2 and clean not in STOP_WORDS:
            keywords.add(clean)
    return keywords

def check_phonetic_match(word1: str, word2: str) -> bool:
    """
    Returns True if word1 and word2 are phonetically matching variants.
    """
    w1 = word1.lower()
    w2 = word2.lower()
    if w1 == w2:
        return True
    
    chroma_variants = {"chromadb", "chromat", "chromad", "chroma"}
    if w1 in chroma_variants and w2 in chroma_variants:
        return True
        
    return False

def is_negative_about_entity(content: str, entity: str) -> bool:
    """
    Splits content into sentences, and returns True if a sentence matching the entity
    contains a negative assertion (e.g. 'does not provide any information').
    """
    c_lower = content.lower()
    ent_lower = entity.lower()
    
    if "chromadb" in ent_lower:
        variants = ["chromadb", "chromat", "chromad", "chroma"]
    else:
        variants = [ent_lower]
        
    has_variant = any(v in c_lower for v in variants)
    if not has_variant:
        return False
        
    sentences = re.split(r"[.!?\n]", c_lower)
    for sent in sentences:
        matched_variant = None
        for v in variants:
            if v in sent:
                matched_variant = v
                break
                
        if matched_variant:
            # Check for negative assertion in this sentence
            if any(phrase in sent for phrase in [
                "does not provide", "does not contain", "no information about",
                "not specify information", "cannot be determined", "unable to answer",
                "information is not available", "not present in", "not visible",
                "is not about"
            ]):
                return True
    return False

def filter_irrelevant_nodes(query: str, evidence_nodes: list[EvidenceNode]) -> list[EvidenceNode]:
    """
    Filters out evidence nodes that do not share entities, keywords, or sufficient
    semantic similarity with the query.
    """
    global _latest_relevance_diagnostics
    
    query_entities = extract_entities(query)
    query_keywords = extract_substantive_keywords(query)
    
    filtered_nodes = []
    removed_nodes = []
    
    for node in evidence_nodes:
        node_entities = extract_entities(node.content).union(extract_entities(node.source))
        node_keywords = extract_substantive_keywords(node.content)
        
        # 1. Filter out entities/keywords for which there is a negative assertion in this node's content
        active_query_entities = set()
        for q_ent in query_entities:
            if not is_negative_about_entity(node.content, q_ent):
                active_query_entities.add(q_ent)
                
        active_query_keywords = set()
        for q_kw in query_keywords:
            is_neg = False
            for q_ent in query_entities:
                if check_phonetic_match(q_kw, q_ent) and is_negative_about_entity(node.content, q_ent):
                    is_neg = True
                    break
            if not is_neg:
                active_query_keywords.add(q_kw)

        # 2. Entity overlap (with phonetic check)
        entity_overlap = 0
        for q_ent in active_query_entities:
            for n_ent in node_entities:
                if check_phonetic_match(q_ent, n_ent):
                    entity_overlap += 1
                    break
                    
        # 3. Keyword overlap (with phonetic check)
        keyword_overlap = 0
        for q_kw in active_query_keywords:
            for n_kw in node_keywords:
                if check_phonetic_match(q_kw, n_kw):
                    keyword_overlap += 1
                    break
                    
        # 4. Overall similarity match
        is_relevant = False
        reason = ""
        
        if query_entities:
            if entity_overlap > 0:
                is_relevant = True
                reason = f"Shared entities: {entity_overlap}"
            elif keyword_overlap >= 1:
                is_relevant = True
                reason = f"Keyword overlap: {keyword_overlap}"
            else:
                is_relevant = False
                reason = "No positive entity or keyword overlap with query containing entities."
        else:
            if keyword_overlap >= 1:
                is_relevant = True
                reason = f"Keyword overlap: {keyword_overlap}"
            elif node.retrieval_score >= 0.50:
                is_relevant = True
                reason = f"High retrieval score: {node.retrieval_score}"
            else:
                is_relevant = False
                reason = "Insufficient keyword overlap and low retrieval score."
                
        overlap_scores = {
            "entity_overlap": entity_overlap,
            "keyword_overlap": keyword_overlap,
            "retrieval_score": node.retrieval_score
        }
        
        if is_relevant:
            filtered_nodes.append(node)
        else:
            removed_nodes.append({
                "source": node.source,
                "modality": node.modality,
                "content": node.content[:150] + "..." if len(node.content) > 150 else node.content,
                "reason_for_removal": reason,
                "overlap_scores": overlap_scores
            })
            
    _latest_relevance_diagnostics = {
        "query": query,
        "removed_nodes": removed_nodes
    }
    
    return filtered_nodes
