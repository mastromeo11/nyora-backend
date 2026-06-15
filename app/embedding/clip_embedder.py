import torch
from transformers import CLIPModel, CLIPProcessor
from PIL import Image

# Singleton CLIP model and processor instances
_clip_model = None
_clip_processor = None

# TODO: Add hardware acceleration support (e.g. CUDA or Apple Silicon MPS)
# TODO: Add batch processing capability for faster bulk image ingestion

def get_clip_resources() -> tuple[CLIPModel, CLIPProcessor]:
    """
    Lazy loads the CLIP model and processor on CPU, caching them for subsequent calls.
    """
    global _clip_model, _clip_processor
    if _clip_model is None or _clip_processor is None:
        model_name = "openai/clip-vit-base-patch32"
        # Load weights lazily from cache / local path
        _clip_model = CLIPModel.from_pretrained(model_name)
        _clip_processor = CLIPProcessor.from_pretrained(model_name)
        _clip_model.eval()
    return _clip_model, _clip_processor

def embed_image(image_path: str) -> list[float]:
    """
    Generates an L2-normalized visual embedding for the given image file.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        list[float]: The normalized 512-dimensional vector.
    """
    model, processor = get_clip_resources()
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
        if hasattr(image_features, "pooler_output"):
            image_features = image_features.pooler_output
        # L2 normalization
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        embedding = image_features[0].tolist()
        
    return embedding

def embed_text_query(text: str) -> list[float]:
    """
    Generates an L2-normalized text embedding in the joint CLIP space.
    
    Args:
        text (str): The search query text.
        
    Returns:
        list[float]: The normalized 512-dimensional vector.
    """
    model, processor = get_clip_resources()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        if hasattr(text_features, "pooler_output"):
            text_features = text_features.pooler_output
        # L2 normalization
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        embedding = text_features[0].tolist()
        
    return embedding

_category_embeddings_cache = {}

def get_category_embeddings() -> dict[str, list[float]]:
    """
    Retrieves and caches the text embeddings for the 9 visual categories.
    """
    global _category_embeddings_cache
    templates = {
        "flowchart": "a flowchart diagram",
        "architecture diagram": "a system architecture diagram",
        "dashboard": "an analytics dashboard interface",
        "graph": "a plotted line graph or coordinate axis",
        "chart": "a pie chart or bar chart",
        "screenshot": "a screenshot of a website or app",
        "document": "a document page with paragraphs of text",
        "table": "a grid table with columns and rows",
        "ui screen": "a user interface screen mockup"
    }
    if not _category_embeddings_cache:
        for cat, prompt in templates.items():
            # Generate normalized CLIP embedding for zero-shot text candidate
            _category_embeddings_cache[cat] = embed_text_query(prompt)
    return _category_embeddings_cache


def classify_image_category(image_path: str) -> str:
    """
    Generates a visual category label for the image using zero-shot CLIP classification
    against the 9 supported classes.
    """
    try:
        img_emb = embed_image(image_path)
        cat_embeddings = get_category_embeddings()
        
        best_cat = "document" # fallback
        best_score = -1.0
        
        for cat, cat_emb in cat_embeddings.items():
            # Dot product of normalized vectors represents cosine similarity
            score = sum(i * t for i, t in zip(img_emb, cat_emb))
            if score > best_score:
                best_score = score
                best_cat = cat
        return best_cat
    except Exception as e:
        print(f"Error during zero-shot image classification: {e}")
        return "document"

