import re

# Mapping of phonetic/OCR/transcription variants to their canonical entity names
ALIAS_TO_CANONICAL = {
    # chromadb
    "chromad": "chromadb",
    "chromat": "chromadb",
    "chroma": "chromadb",
    "chromadb": "chromadb",
    # ollama
    "olama": "ollama",
    "ollamaa": "ollama",
    "ollama": "ollama",
    # llama3.1
    "olama3": "llama3.1",
    "llama": "llama3.1",
    "llama3.1": "llama3.1",
    # fastapi
    "fastapi": "fastapi",
    # clip
    "clip": "clip",
    # whisper
    "whisper": "whisper",
    # vector
    "vector": "vector",
    # embedding
    "embedding": "embedding",
    # sustainable
    "sustainable": "sustainable",
    # city
    "city": "city",
    # meeting
    "meeting": "meeting",
    # alert
    "alert": "alert",
    # error": "error",
    "error": "error",
    # dashboard
    "dashboard": "dashboard",
    # nodes
    "nodes": "nodes",
    # flowchart
    "flowchart": "flowchart",
    # table
    "table": "table",
    # investment
    "investment": "investment"
}

def normalize_entity(name: str) -> str:
    """
    Normalizes any entity name or alias to its canonical representation.
    """
    cleaned = name.strip().lower()
    return ALIAS_TO_CANONICAL.get(cleaned, cleaned)

def get_node_entities(content: str) -> set[str]:
    """
    Scans content for canonical entity names or their known aliases,
    returning a set of all canonical entities matched.
    """
    found = set()
    content_lower = content.lower()
    
    entity_groups = {
        "chromadb": ["chromadb", "chromad", "chromat", "chroma"],
        "ollama": ["ollama", "olama", "ollamaa"],
        "llama3.1": ["llama3.1", "olama3", "llama"],
        "fastapi": ["fastapi"],
        "clip": ["clip"],
        "whisper": ["whisper"],
        "vector": ["vector"],
        "embedding": ["embedding"],
        "sustainable": ["sustainable"],
        "city": ["city"],
        "meeting": ["meeting"],
        "alert": ["alert"],
        "error": ["error"],
        "dashboard": ["dashboard"],
        "nodes": ["nodes"],
        "flowchart": ["flowchart"],
        "table": ["table"],
        "investment": ["investment"]
    }
    
    for canonical, aliases in entity_groups.items():
        for alias in aliases:
            # We do a simple substring match consistent with current RAG project logic,
            # but using word boundaries when the alias is short to prevent false positives.
            if len(alias) <= 3:
                # Use regex with word boundaries for very short aliases
                if re.search(rf"\b{alias}\b", content_lower):
                    found.add(canonical)
                    break
            else:
                if alias in content_lower:
                    found.add(canonical)
                    break
                    
    return found
