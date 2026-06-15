import re
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.context_builder import get_node_entities

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

def clean_word(word: str) -> str:
    return re.sub(r"[^\w]", "", word).lower()

def extract_substantive_keywords(sentence: str) -> list[str]:
    words = sentence.split()
    keywords = []
    for w in words:
        clean = clean_word(w)
        if len(clean) > 2 and clean not in STOP_WORDS:
            keywords.append(clean)
    return keywords

def validate_grounding(
    answer: str,
    ranked_evidence: list[EvidenceNode],
    observations: list = None,
    reflections: list = None
) -> tuple[str, list[dict]]:
    """
    Splits the answer into claims, maps each claim to entity-specific evidence,
    and validates them. Bypasses check if the answer is already the fallback.
    
    If supported ratio < 0.6, overrides the answer with:
    "The information is not available in the provided documents."
    """
    fallback_string = "The information is not available in the provided documents."
    if answer.strip().lower() == fallback_string.lower():
        return fallback_string, []
        
    sentences = re.split(r"(?<=[.!?]) +", answer)
    report = []
    
    total_substantive = 0
    supported_substantive = 0
    
    for idx, sent in enumerate(sentences):
        sent_str = sent.strip()
        if not sent_str:
            continue
            
        claim_entities = get_node_entities(sent_str)
        keywords = extract_substantive_keywords(sent_str)
        
        if not keywords:
            # Non-substantive filler/introductory sentence
            status = "Supported"
        else:
            total_substantive += 1
            
            # 1. Map to entity-specific nodes
            if claim_entities:
                matching_nodes = []
                for node in ranked_evidence:
                    node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
                    if claim_entities.intersection(node_ents):
                        matching_nodes.append(node)
            else:
                matching_nodes = ranked_evidence
                
            if not matching_nodes:
                if observations or reflections:
                    matching_text = ""
                else:
                    status = "Unsupported"
                    matching_text = None
            else:
                # Combine matching evidence text
                matching_text = " ".join([node.content for node in matching_nodes]).lower()
                
            if matching_text is not None:
                # Also include observations and reflections content
                if observations:
                    obs_text = " ".join([
                        (o.get("content", "") if isinstance(o, dict) else getattr(o, "content", str(o))) 
                        for o in observations
                    ]).lower()
                    matching_text += " " + obs_text
                if reflections:
                    refl_text = " ".join([
                        (r.get("reason", "") if isinstance(r, dict) else getattr(r, "reason", str(r)))
                        for r in reflections
                    ]).lower()
                    matching_text += " " + refl_text
                
                # Check keyword overlap against matching text (allowing phonetic match for chromat/chromadb)
                matched_keywords = []
                for kw in keywords:
                    if kw in matching_text:
                        matched_keywords.append(kw)
                    elif "chroma" in kw and ("chromat" in matching_text or "chroma" in matching_text):
                        matched_keywords.append(kw)
                    elif "chromat" in kw and ("chromadb" in matching_text or "chroma" in matching_text):
                        matched_keywords.append(kw)
                        
                match_ratio = len(matched_keywords) / len(keywords)
                
                if match_ratio >= 0.90:
                    status = "Supported"
                    supported_substantive += 1
                elif match_ratio > 0.0:
                    status = "Partially Supported"
                    supported_substantive += 1
                else:
                    status = "Unsupported"
                    
        report.append({
            "claim_index": idx + 1,
            "claim": sent_str,
            "status": status,
            "keywords": keywords,
            "entities": sorted(list(claim_entities))
        })
        
    # Supported claim ratio check
    ratio = 1.0
    if total_substantive > 0:
        ratio = supported_substantive / total_substantive
        
    if ratio < 0.60:
        return fallback_string, report
    else:
        return answer, report
