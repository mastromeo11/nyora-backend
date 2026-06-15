import re
import requests
from app.config import OLLAMA_URL, LLM_MODEL

def detect_query_type(query: str) -> str:
    """
    Classifies a query into TEXT, VISUAL, or MULTIMODAL.
    
    Stage 1: Fast regex/keyword checks.
    Stage 2: Few-shot query routing via local LLM (Phi-3) fallback.
    """
    q = query.lower().strip()
    
    # --- STAGE 1: Fast Regex / Keyword Detection ---
    visual_regex = [
        r"\bhow many (circular|rect|circle|bar|node|line|column|row|box|block|arrow)s?\b",
        r"\bwhich (bar|column|row|box|circle|diagram|screenshot|image|photo|picture|label|shape|node)s?\b",
        r"\bwhat is inside the (left|right|top|bottom|middle|blue|green|red|grey|gray) (box|block|circle|node|rectangle)s?\b",
        r"\bwhat error message is shown\b",
        r"\bshown inside\b",
        r"\bshown in\b",
        r"\bvisible in\b",
        r"\bwhat does this image\b"
    ]
    
    for pattern in visual_regex:
        if re.search(pattern, q):
            return "VISUAL"
            
    visual_words = ["circles", "circular nodes", "tallest bar", "tallest", "highest bar", "what shape", "what color"]
    if any(w in q for w in visual_words):
        return "VISUAL"
        
    visual_terms = [
        "diagram", "flowchart", "architecture", "table", "dashboard", "screenshot", "image", "picture", "photo",
        "shown", "box", "circle", "bar", "column", "row", "component", "connects", "connect", "connection", "node",
        "chart", "graph", "bars", "circles", "nodes", "layout", "error message"
    ]
    has_visual_term = any(t in q for t in visual_terms)
    
    # If no visual terms are present, it is standard TEXT.
    if not has_visual_term:
        return "TEXT"
        
    # If query contains visual terms AND text-focused informational keywords, it is MULTIMODAL
    multimodal_keywords = [
        "tell me", "list", "explain", "what is", "summarize", "describe", "summary", "how does", "how do", 
        "where does", "where do", "overview", "details", "info", "information"
    ]
    if any(w in q for w in multimodal_keywords):
        return "MULTIMODAL"
        
    # --- STAGE 2: Local Phi-3 Classifier Fallback ---
    try:
        system_instruction = (
            "You are a precise routing assistant. Classify the user query into one of these three categories:\n"
            "1. TEXT: queries about facts, definitions, meeting details, or text documents (e.g. \"What is ChromaDB?\", \"What investment was approved?\").\n"
            "2. VISUAL: queries asking about visual content, layout, colors, shape counts, or text specifically shown inside a diagram, image, flowchart, table, dashboard, or screenshot (e.g. \"Which database is shown?\", \"Which component connects to Ollama?\", \"What is inside the left box?\").\n"
            "3. MULTIMODAL: queries combining document facts with visual image content.\n\n"
            "Respond with exactly one word: \"TEXT\", \"VISUAL\", or \"MULTIMODAL\"."
        )
        prompt = f"Query: \"{query}\"\nCategory:"
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "system": system_instruction,
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            },
            timeout=5
        )
        if response.status_code == 200:
            classification = response.json().get("response", "").strip().upper()
            classification = re.sub(r'[^A-Z]', '', classification)
            if classification in ["TEXT", "VISUAL", "MULTIMODAL"]:
                return classification
    except Exception as e:
        print(f"Stage 2 classification failed: {e}")
        
    # Heuristic fallback if LLM times out or fails
    if "diagram" in q or "flowchart" in q or "table" in q or "dashboard" in q:
        return "VISUAL"
        
    return "TEXT"
