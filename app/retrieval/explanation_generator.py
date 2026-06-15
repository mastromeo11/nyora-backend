def generate_visual_explanation(clip_score: float, visual_category: str, is_fallback: bool, selected_rank: int) -> str:
    """
    Generates a structured human-readable justification for visual matching and citation choices.
    """
    if is_fallback:
        return f"Fallback answer returned because no valid visual detail could be confirmed. Top candidate (rank #1) was selected as citation."
        
    category_phrase = f"matched visual category '{visual_category}'" if visual_category else "matched query semantics"
    return (
        f"Grounded visual match from candidate rank #{selected_rank}. "
        f"Selected because it {category_phrase} with a CLIP similarity score of {clip_score:.4f} and returned a valid answer."
    )

def generate_multimodal_explanation(text_score: float, visual_score: float, visual_category: str) -> str:
    """
    Generates a human-readable justification statement for multimodal fusion results.
    """
    category_phrase = f" | Visual category: '{visual_category}'" if visual_category else ""
    return (
        f"Unified Multimodal Match. Text Match: BGE Score {text_score:.2f} (60% weight); "
        f"Visual Match: CLIP Score {visual_score:.2f} (40% weight){category_phrase}."
    )
