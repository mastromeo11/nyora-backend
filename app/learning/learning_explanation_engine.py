from typing import List, Dict, Any

def compile_learning_explanation(patterns: List[Dict[str, Any]], corrections: List[Dict[str, Any]]) -> str:
    """
    Compiles natural, explainable summaries indicating how historical learning patterns
    and correction records influenced the retrieval context, concealing internal thoughts.
    """
    explanations = []

    # 1. Summarize patterns
    if patterns:
        all_entities = set()
        for pat in patterns:
            for ent in pat.get("supporting_entities", []):
                all_entities.add(ent.upper())
                
        if all_entities:
            ent_str = ", ".join(sorted(list(all_entities))[:4])
            explanations.append(f"Similar previous queries successfully retrieved evidence related to {ent_str}.")

    # 2. Summarize corrections
    if corrections:
        reasons = []
        for corr in corrections:
            reason = corr.get("reason", "")
            if reason:
                reasons.append(f"'{reason}'")
                
        if reasons:
            reasons_str = ", ".join(reasons[:2])
            explanations.append(f"Earlier corrections resolved execution issues on {reasons_str} to refine plan selection.")

    if not explanations:
        return "No historical learning patterns or corrections were relevant to this query."

    return " ".join(explanations)
