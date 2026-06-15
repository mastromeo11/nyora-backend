import re

ALIAS_TO_CANONICAL = {
    "chromat": "chromadb",
    "chromad": "chromadb",
    "chroma": "chromadb",
    "chromadb": "chromadb",
    
    "olama": "ollama",
    "ollamaa": "ollama",
    "ollama3": "ollama",
    "ollama 3.1": "ollama",
    "ollama": "ollama",
    
    "fast api": "fastapi",
    "fastapi app": "fastapi",
    "fastapi": "fastapi",
    
    "llama": "llama3.1",
    "llama3.1": "llama3.1",
    "clip": "clip",
    "whisper": "whisper",
    "vector": "vector",
    "embedding": "embedding",
    "sustainable": "sustainable",
    "city": "city",
    "meeting": "meeting",
    "alert": "alert",
    "error": "error",
    "dashboard": "dashboard",
    "nodes": "nodes",
    "flowchart": "flowchart",
    "table": "table",
    "investment": "investment"
}

def normalize_entity_name(name: str) -> str:
    """
    Normalizes any entity name or alias to its canonical representation.
    """
    cleaned = name.strip().lower()
    return ALIAS_TO_CANONICAL.get(cleaned, cleaned)

def get_canonical_entities(content: str) -> set[str]:
    """
    Scans content for canonical entity names or their known aliases,
    returning a set of all canonical entities matched.
    """
    found = set()
    content_lower = content.lower()
    
    entity_groups = {
        "chromadb": ["chromadb", "chromad", "chromat", "chroma"],
        "ollama": ["ollama", "olama", "ollamaa", "ollama3", "ollama 3.1"],
        "fastapi": ["fastapi", "fast api", "fastapi app"],
        "llama3.1": ["llama3.1", "llama"],
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
            if len(alias) <= 3:
                if re.search(rf"\b{alias}\b", content_lower):
                    found.add(canonical)
                    break
            else:
                if alias in content_lower:
                    found.add(canonical)
                    break
                    
    return found
