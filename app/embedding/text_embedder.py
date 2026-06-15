from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

# Lazy loading for the SentenceTransformer model
_model = None

def _get_model():
    global _model
    if _model is None:
        print(f"Loading Text Embedder model: {EMBEDDING_MODEL}...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Text Embedder model loaded successfully.")
    return _model

def embed_text(texts: list[str]) -> list:
    """
    Generates BGE embeddings for a list of texts.
    Returns a list of list of floats.
    """
    try:
        model = _get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    except Exception as e:
        print(f"Error generating BGE text embeddings: {e}")
        # Return a list of zero vectors matching model dimensions (384 for bge-small) as fallback
        return [[0.0] * 384 for _ in texts]

# TODO: Implement CLIP visual embedding model (Milestone 6)
# class ClipEmbedder:
#     pass
