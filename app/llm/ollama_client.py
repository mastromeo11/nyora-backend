import requests
from app.config import OLLAMA_URL, LLM_MODEL
from app.llm.base import BaseLLMClient

class OllamaClient(BaseLLMClient):
    """
    Local LLM generation wrapper leveraging Ollama's REST API.
    """
    def __init__(self, url: str = OLLAMA_URL, model: str = LLM_MODEL):
        self.url = url
        self.model = model

    def generate_response(self, query: str, context: str, allow_empty_context: bool = False) -> str:
        """
        Sends the query and retrieved context to Ollama for local generation.
        Strictly restricts generation to the provided context unless allow_empty_context is True.
        """
        if not allow_empty_context and (not context or not context.strip()):
            return "The information is not available in the provided documents."

        if allow_empty_context:
            prompt = query.strip()
            system_instruction = "You are a helpful assistant. Answer the user's prompt directly, following any formatting rules requested."
        else:
            # Prompt construction
            prompt = (
                f"Context:\n"
                f"----------------\n"
                f"{context.strip()}\n"
                f"----------------\n\n"
                f"Question:\n"
                f"{query.strip()}\n\n"
                f"Answer:"
            )

            system_instruction = (
                "You are a helpful assistant. Use ONLY the supplied context to answer the question. "
                "Note: The context contains OCR text from diagrams. Words appearing next to each other represent connected components (for example, in 'Ollama Query API Llama3.1', Llama3.1 is the model associated with Ollama). "
                "Never invent information. Keep your response brief and direct. If the answer is not found in the context, "
                "you MUST respond exactly with: "
                "\"The information is not available in the provided documents.\""
            )


        try:
            print(f"\n[DEBUG OLLAMA] Sending prompt:\n{prompt}\n")
            print(f"[DEBUG OLLAMA] System instruction:\n{system_instruction}\n")
            
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_instruction,
                    "stream": False,
                    "options": {
                        "temperature": 0.0  # Force deterministic groundedness
                    }
                },
                timeout=30  # Timeout protection
            )
            
            # Handle model not found error
            if response.status_code == 404:
                return f"Error: The model '{self.model}' was not found. Please run 'ollama pull {self.model}' first."
                
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "").strip()
            
            print(f"[DEBUG OLLAMA] Raw response from Ollama: '{answer}'\n")
            
            if not answer:
                return "The information is not available in the provided documents."

                
            # Post-processing heuristic to guarantee exact fallback string
            if not allow_empty_context:
                lowered_answer = answer.lower()
                if any(phrase in lowered_answer for phrase in [
                    "not available in the provided documents",
                    "not found in the context",
                    "not mentioned in the context",
                    "does not contain details",
                    "is not mentioned",
                    "does not mention",
                    "information provided does not contain"
                ]):
                    return "The information is not available in the provided documents."
                
            return answer

        except requests.exceptions.ConnectionError:
            print(f"\n[Warning] Connection Error: Ollama server is offline or unavailable at {self.url}.")
            return "Error: Local Ollama server is not running. Please launch it to complete local generation."
            
        except requests.exceptions.Timeout:
            print(f"\n[Warning] Timeout Error: Ollama query timed out after 30 seconds.")
            return "Error: Local generation timed out."
            
        except Exception as e:
            print(f"\n[Warning] Unexpected generation error: {e}")
            return f"Error: Generation failed due to an unexpected error ({str(e)})."

# TODO: Implement GeminiClient inheriting from BaseLLMClient
# class GeminiClient(BaseLLMClient):
#     pass

# TODO: Implement OpenAIClient inheriting from BaseLLMClient
# class OpenAIClient(BaseLLMClient):
#     pass

# TODO: Implement ClaudeClient inheriting from BaseLLMClient
# class ClaudeClient(BaseLLMClient):
#     pass

# Shared client instance
ollama_client = OllamaClient()
