from abc import ABC, abstractmethod
from typing import Any, Optional

class AbstractVisionModel(ABC):
    """
    Abstract interface for vision models (CLIP, LLaVA, Qwen2.5-VL, MiniCPM-V, etc.)
    to ensure seamless compatibility with future vision-language integrations.
    """
    
    @abstractmethod
    def embed_image(self, image_path: str) -> list[float]:
        """Generate a visual embedding vector for an image."""
        pass
        
    @abstractmethod
    def generate_caption(self, image_path: str, prompt: Optional[str] = None) -> str:
        """Generate a description or caption for the image (for VLMs)."""
        pass
        
    @abstractmethod
    def visual_qa(self, image_path: str, question: str) -> str:
        """Ask a visual question about the image (for VLMs)."""
        pass

class CLIPModelWrapper(AbstractVisionModel):
    """
    Wrapper for standard OpenAI CLIP Model.
    Note: Standard CLIP only supports image embedding. Captioning and Visual QA 
    methods are supported via zero-shot classification and fallback descriptions.
    """
    def embed_image(self, image_path: str) -> list[float]:
        from app.embedding.clip_embedder import embed_image
        return embed_image(image_path)
        
    def generate_caption(self, image_path: str, prompt: Optional[str] = None) -> str:
        from app.embedding.clip_embedder import classify_image_category
        category = classify_image_category(image_path)
        return f"An image categorized as a '{category}' using zero-shot CLIP classification."
        
    def visual_qa(self, image_path: str, question: str) -> str:
        return (
            "Visual Q&A is not supported natively by the CLIP vision model. "
            "Please configure a Vision-Language Model (like LLaVA, Qwen-VL) to execute detailed visual queries."
        )

class LLaVAModelWrapper(AbstractVisionModel):
    """
    Placeholder wrapper for future LLaVA integration.
    """
    def embed_image(self, image_path: str) -> list[float]:
        # Return dummy empty embedding or proxy CLIP embedding
        raise NotImplementedError("LLaVA model visual embedding is not yet configured.")
        
    def generate_caption(self, image_path: str, prompt: Optional[str] = None) -> str:
        return "[LLaVA Caption Placeholder] A high-resolution system diagram detailing workflow components."
        
    def visual_qa(self, image_path: str, question: str) -> str:
        return f"[LLaVA Visual QA Placeholder] Answer to question '{question}' about the image."

class QwenVLModelWrapper(AbstractVisionModel):
    """
    Placeholder wrapper for future Qwen2.5-VL integration.
    """
    def embed_image(self, image_path: str) -> list[float]:
        raise NotImplementedError("Qwen2.5-VL model visual embedding is not yet configured.")
        
    def generate_caption(self, image_path: str, prompt: Optional[str] = None) -> str:
        return "[Qwen2.5-VL Caption Placeholder] Technical dashboard mockup showing user metrics and pie chart slices."
        
    def visual_qa(self, image_path: str, question: str) -> str:
        return f"[Qwen2.5-VL Visual QA Placeholder] Answer to question '{question}' about the image."

class MiniCPMModelWrapper(AbstractVisionModel):
    """
    Placeholder wrapper for future MiniCPM-V integration.
    """
    def embed_image(self, image_path: str) -> list[float]:
        raise NotImplementedError("MiniCPM-V model visual embedding is not yet configured.")
        
    def generate_caption(self, image_path: str, prompt: Optional[str] = None) -> str:
        return "[MiniCPM-V Caption Placeholder] A software user interface showing tables, labels and buttons."
        
    def visual_qa(self, image_path: str, question: str) -> str:
        return f"[MiniCPM-V Visual QA Placeholder] Answer to question '{question}' about the image."
