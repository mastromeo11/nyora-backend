import re
from typing import Tuple

SENSITIVE_PATTERNS = [
    # Phone numbers
    r"\b(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b",
    # Emails
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    # Passwords and API keys
    r"(?i)\b(api[-_]?key|password|secret|token|credential|auth[-_]?key)\b\s*(?:[:=]|\bis\b)?\s*\S+",
]

SENSITIVE_KEYWORDS = {
    # Religion
    "christian", "muslim", "islam", "jewish", "hindu", "buddhist", "atheist", "god", 
    "church", "mosque", "temple", "bible", "quran", "religion",
    # Politics
    "democrat", "republican", "liberal", "conservative", "communism", "socialism", 
    "election", "vote", "politics", "president", "biden", "trump", "political",
    # Diagnoses
    "cancer", "diabetes", "depression", "anxiety", "adhd", "hiv", "aids", "disease", 
    "illness", "diagnose", "patient", "medical", "diagnosis",
    # Sexual Orientation / Criminal history
    "gay", "lesbian", "bisexual", "transgender", "queer", "heterosexual", "homosexual", 
    "sexual orientation", "criminal", "felony", "arrest"
}

def filter_sensitive_info(text: str) -> Tuple[str, bool]:
    """
    Detects and strips sensitive properties. Replaces matches with '[FILTERED]'.
    Returns the filtered text and a boolean flag indicating if filtering occurred.
    """
    if not text:
        return text, False
        
    filtered = False
    
    # 1. Match regex patterns
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text):
            text = re.sub(pattern, "[FILTERED]", text)
            filtered = True
            
    # 2. Match exact keywords
    words = re.split(r"(\W+)", text)
    for i, w in enumerate(words):
        if w.lower() in SENSITIVE_KEYWORDS:
            words[i] = "[FILTERED]"
            filtered = True
            
    text = "".join(words)
    # Simplify consecutive [FILTERED] tags
    text = re.sub(r"\[FILTERED\](\s*\[FILTERED\])+", "[FILTERED]", text)
    
    return text, filtered
