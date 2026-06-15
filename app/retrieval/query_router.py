from datetime import datetime
from app.config import LLM_MODEL
from app.retrieval.intent_detector import detect_query_type
from app.retrieval.text_retriever import retrieve_text
from app.retrieval.fusion_retriever import retrieve_multimodal
from app.retrieval.visual_qa_pipeline import answer_visual_question
from app.llm.ollama_client import ollama_client

from app.retrieval.unified_pipeline import answer_query
from app.retrieval.intent_detector import detect_query_type

def route_query(query: str) -> dict:
    """
    Routes query by converging all pathways (TEXT, VISUAL, MULTIMODAL)
    into the Unified Evidence RAG engine.
    """
    intent = detect_query_type(query)
    res = answer_query(query)
    res["intent"] = intent
    return res
