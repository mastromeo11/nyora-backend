import os
import requests
import base64
from app.config import VISION_MODEL, VISION_URL

class BaseVisionModel:
    """
    Abstract interface for offline vision-language models.
    """
    def visual_qa(self, image_path: str, question: str) -> str:
        raise NotImplementedError
        
    def caption(self, image_path: str) -> str:
        raise NotImplementedError
        
    def describe(self, image_path: str) -> str:
        raise NotImplementedError

class LlavaModelWrapper(BaseVisionModel):
    """
    Wrapper for LLaVA visual inference served through local Ollama.
    """
    def __init__(self, model: str = VISION_MODEL, url: str = VISION_URL):
        self.model = model
        self.url = url

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def visual_qa(self, image_path: str, question: str) -> str:
        try:
            if not os.path.exists(image_path):
                return "The information is not visible in the image."
                
            base64_img = self._encode_image(image_path)
            system_instruction = (
                "You are a visual assistant.\n"
                "Answer ONLY from the supplied image.\n"
                "Never assume facts.\n"
                "Never use external knowledge.\n"
                "If the answer is not visible, reply exactly:\n"
                "\"The information is not visible in the image.\""
            )
            
            prompt = f"Question: {question}\nAnswer:"
            
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_instruction,
                    "images": [base64_img],
                    "stream": False,
                    "options": {
                        "temperature": 0.0
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            answer = response.json().get("response", "").strip()
            
            # Post-processing heuristic to guarantee exact fallback string
            lowered_answer = answer.lower()
            if any(phrase in lowered_answer for phrase in [
                "not visible",
                "cannot be determined from the image",
                "not specified in the image",
                "does not show",
                "not present in the image",
                "information is not available",
                "no information",
                "unable to answer",
                "cannot answer"
            ]):
                return "The information is not visible in the image."
                
            return answer
        except Exception as e:
            print(f"Llava VQA Error for {image_path}: {e}")
            return "The information is not visible in the image."

    def caption(self, image_path: str) -> str:
        try:
            if not os.path.exists(image_path):
                return "A visual document."
                
            base64_img = self._encode_image(image_path)
            prompt = (
                "Describe the contents of this image in a single detailed sentence. "
                "Focus on technical components, diagram elements, flowcharts, titles, and text labels."
            )
            
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [base64_img],
                    "stream": False,
                    "options": {
                        "temperature": 0.0
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Llava Caption Error for {image_path}: {e}")
            return "A visual document."

    def describe(self, image_path: str) -> str:
        return self.caption(image_path)

class QwenVLModelWrapper(BaseVisionModel):
    """
    Placeholder wrapper for future Qwen-VL model support.
    """
    def visual_qa(self, image_path: str, question: str) -> str:
        return "[Qwen-VL Visual QA Placeholder] Answer to question."
        
    def caption(self, image_path: str) -> str:
        return "[Qwen-VL Caption Placeholder]"
        
    def describe(self, image_path: str) -> str:
        return "[Qwen-VL Description]"

class MiniCPMVModelWrapper(BaseVisionModel):
    """
    Placeholder wrapper for future MiniCPM-V model support.
    """
    def visual_qa(self, image_path: str, question: str) -> str:
        return "[MiniCPM-V Visual QA Placeholder] Answer to question."
        
    def caption(self, image_path: str) -> str:
        return "[MiniCPM-V Caption Placeholder]"
        
    def describe(self, image_path: str) -> str:
        return "[MiniCPM-V Description]"
