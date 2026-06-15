# Source quality weights representing structural reliability of each modality
SOURCE_QUALITY_WEIGHTS = {
    "pdf": 1.0,
    "docx": 0.95,
    "ocr": 0.85,
    "image": 0.80,
    "caption": 0.80,
    "vqa": 0.80,
    "audio": 0.75
}

def get_source_quality(modality_type: str) -> float:
    """
    Returns the static quality weight/prior for a given modality type.
    """
    return SOURCE_QUALITY_WEIGHTS.get(modality_type.lower(), 0.70)
