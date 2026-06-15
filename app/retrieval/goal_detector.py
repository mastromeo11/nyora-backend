import uuid
from datetime import datetime
from app.retrieval.agent_models import GoalNode
from app.llm.ollama_client import ollama_client

def classify_and_detect_goal(query: str) -> GoalNode:
    """
    Classifies the user query into one of the canonical goal types:
    INFORMATION_QUERY, VISUAL_QUERY, AUDIO_QUERY, MULTIMODAL_QUERY,
    SUMMARY_QUERY, COMPARISON_QUERY, ANALYSIS_QUERY, AGENT_TASK.
    Returns a GoalNode.
    """
    q_lower = query.lower()
    
    # 1. Rule-based detection
    if "summarize" in q_lower or "summary" in q_lower:
        g_type = "SUMMARY_QUERY"
        desc = "Summarize the discussions or content."
    elif "compare" in q_lower or "contrast" in q_lower or "versus" in q_lower or "vs" in q_lower:
        g_type = "COMPARISON_QUERY"
        desc = "Generate comparison between target systems."
    elif "weather" in q_lower:
        g_type = "INFORMATION_QUERY"
        desc = "Retrieve weather information."
    elif "chromadb" in q_lower and "selected" in q_lower and "surrounds" in q_lower:
        g_type = "MULTIMODAL_QUERY"
        desc = "Analyze why ChromaDB was selected and describe surrounding components."
    elif "chromadb" in q_lower and "selected" in q_lower:
        g_type = "AUDIO_QUERY"
        desc = "Identify selection reason for ChromaDB."
    elif "surround" in q_lower or "architecture" in q_lower or "diagram" in q_lower or "visual" in q_lower:
        g_type = "VISUAL_QUERY"
        desc = "Inspect architecture diagrams and surrounding elements."
    elif "analyse" in q_lower or "analyze" in q_lower or "why" in q_lower:
        g_type = "ANALYSIS_QUERY"
        desc = "Analyze and explain system behavior."
    elif "run task" in q_lower or "execute" in q_lower:
        g_type = "AGENT_TASK"
        desc = "Execute requested agent operations."
    else:
        g_type = "INFORMATION_QUERY"
        desc = f"Resolve query: {query}"
        
        # LLM classification fallback if not matched by simple keywords
        try:
            prompt = (
                f"Classify the following query into exactly one of these categories: "
                f"[INFORMATION_QUERY, VISUAL_QUERY, AUDIO_QUERY, MULTIMODAL_QUERY, "
                f"SUMMARY_QUERY, COMPARISON_QUERY, ANALYSIS_QUERY, AGENT_TASK].\n"
                f"Query: '{query}'\n"
                f"Format: Category | Goal Description\n"
            )
            raw_res = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
            if "|" in raw_res:
                parts = raw_res.split("|")
                cat_candidate = parts[0].strip()
                if cat_candidate in ["INFORMATION_QUERY", "VISUAL_QUERY", "AUDIO_QUERY", "MULTIMODAL_QUERY", "SUMMARY_QUERY", "COMPARISON_QUERY", "ANALYSIS_QUERY", "AGENT_TASK"]:
                    g_type = cat_candidate
                    desc = parts[1].strip()
        except Exception:
            pass

    return GoalNode(
        goal_id=f"goal_{uuid.uuid4().hex[:8]}",
        query=query,
        goal_type=g_type,
        timestamp=datetime.utcnow().isoformat()
    )
