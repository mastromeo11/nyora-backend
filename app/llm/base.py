from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    """
    Abstract Base Class for local and future cloud LLM providers (Gemini, OpenAI, Claude).
    Ensures extensible and consistent signatures across different language model backends.
    """
    @abstractmethod
    def generate_response(self, query: str, context: str, allow_empty_context: bool = False) -> str:
        """
        Generates a grounded natural language response from a given user query and context.
        
        Args:
            query (str): The search question or user query.
            context (str): The concatenated relevant document chunks.
            
        Returns:
            str: The generated response.
        """
        pass
