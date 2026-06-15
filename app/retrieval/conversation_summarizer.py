from datetime import datetime
import json
import os
from app.retrieval.session_memory import get_session
from app.retrieval.memory_cache import get_session_cache, save_session_cache
from app.llm.ollama_client import ollama_client
from app.retrieval.entity_alias_map import get_node_entities
from app.config import SUMMARY_INTERVAL
from app.retrieval.memory_metrics import increment_summary

def summarize_session_if_needed(session_id: str):
    """
    Checks if the number of turns in the session is a multiple of SUMMARY_INTERVAL.
    If yes, triggers generation of a new persistent ConversationSummary.
    """
    turns = get_session(session_id)
    if not turns:
        return
        
    num_turns = len(turns)
    if num_turns > 0 and num_turns % SUMMARY_INTERVAL == 0:
        print(f"[SUMMARIZER] Summarizing session {session_id} because turn count {num_turns} reached interval {SUMMARY_INTERVAL}")
        generate_conversation_summary(session_id, turns)

def generate_conversation_summary(session_id: str, turns: list):
    """
    Generates a ConversationSummary for the session based on the latest SUMMARY_INTERVAL turns.
    """
    # Get the block of turns to summarize (the last SUMMARY_INTERVAL turns)
    block_turns = turns[-SUMMARY_INTERVAL:]
    
    # Format turns for prompt
    history_lines = []
    for turn in block_turns:
        history_lines.append(f"User: {turn.user_query}")
        history_lines.append(f"Assistant: {turn.assistant_answer}")
    history_text = "\n".join(history_lines)
    
    prompt = f"""You are an assistant that summarizes conversations and extracts key technical facts.
Analyze the following conversation block and output two things:
1. A brief summary of the conversation in a single short sentence.
2. A list of key technical facts or components discussed (such as ChromaDB, FastAPI, Ollama).

Format your output exactly as follows:
Summary: <single sentence summary>
Facts:
- <fact 1>
- <fact 2>

Conversation block:
{history_text}
"""

    try:
        raw_res = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
        lines = raw_res.strip().split("\n")
        
        summary_line = ""
        facts = []
        
        in_facts = False
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
            if line_strip.lower().startswith("summary:"):
                summary_line = line_strip[len("summary:"):].strip()
                in_facts = False
            elif line_strip.lower().startswith("facts:"):
                in_facts = True
            elif in_facts:
                if line_strip.startswith("-"):
                    fact = line_strip[1:].strip()
                elif line_strip.startswith("*"):
                    fact = line_strip[1:].strip()
                else:
                    fact = line_strip
                if fact:
                    facts.append(fact)
                    
        if not summary_line:
            # Fallback parser if summary wasn't marked with prefix
            # Try to grab the first non-empty line as summary
            for line in lines:
                if line.strip() and not line.strip().lower().startswith("facts") and not line.strip().startswith("-"):
                    summary_line = line.strip()
                    break
            if not summary_line:
                summary_line = "Discussion about system components and integration."
                
        # Extract entity focus from these turns
        ents = set()
        for turn in block_turns:
            ents = ents.union(get_node_entities(turn.user_query)).union(get_node_entities(turn.assistant_answer))
            
        session_data = get_session_cache(session_id)
        summaries = session_data.setdefault("summaries", [])
        
        new_summary = {
            "session_id": session_id,
            "summary": summary_line,
            "entity_focus": sorted(list(ents)),
            "important_facts": facts if facts else ["Discussion covered database and web framework interaction."],
            "timestamp": datetime.utcnow().isoformat()
        }
        summaries.append(new_summary)
        save_session_cache(session_id, session_data)
        
        # Track metrics
        increment_summary()
        
        print(f"[SUMMARIZER] Generated summary: '{summary_line}' | Facts count: {len(facts)}")
        
    except Exception as e:
        print(f"[SUMMARIZER] Error generating conversation summary: {e}")
