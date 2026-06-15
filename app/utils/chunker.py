from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Splits text into chunks of `chunk_size` words, overlapping by `overlap` words.
    
    Args:
        text (str): The raw text to split.
        chunk_size (int): The number of words in each chunk.
        overlap (int): The number of overlapping words between consecutive chunks.
        
    Returns:
        list[str]: A list of text chunks.
    """
    if not text or not text.strip():
        return []
        
    words = text.strip().split()
    if len(words) <= chunk_size:
        return [text.strip()]
        
    chunks = []
    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size // 2  # Fallback to prevent infinite loops
        
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        i += step
        
    return chunks
