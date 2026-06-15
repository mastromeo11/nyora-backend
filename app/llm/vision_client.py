import os
from app.llm.vision_model import LlavaModelWrapper
from app.llm.vqa_cache import get_cached_answer, store_cached_answer
from app.config import ENABLE_VQA_CACHE

# Singleton vision model client wrapper instance
_vision_model_instance = LlavaModelWrapper()

def ask_image_question(image_path: str, question: str) -> str:
    """
    Sends a query and image path to the local VLM to perform grounded Visual QA.
    Repeated queries bypass VLM using the cached answer.
    """
    image_id = os.path.basename(image_path)
    
    if ENABLE_VQA_CACHE:
        cached = get_cached_answer(question, image_id)
        if cached is not None:
            return cached
            
    ans = _vision_model_instance.visual_qa(image_path, question)
    
    if ENABLE_VQA_CACHE:
        store_cached_answer(question, image_id, ans)
        
    return ans

def generate_image_caption(image_path: str) -> str:
    """
    Prompts the local VLM to generate a descriptive caption for the image contents.
    """
    return _vision_model_instance.caption(image_path)
