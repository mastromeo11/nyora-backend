from typing import Any, List, Optional
from app.retrieval.evidence_models import EvidenceNode
from app.retrieval.entity_alias_map import get_node_entities

def _build_evidence_context(ranked_evidence: List[EvidenceNode], query: str = None) -> str:
    """
    Helper function containing the original entity-centric evidence context construction.
    """
    query_entities = get_node_entities(query) if query else set()
    
    # If the query mentions no predefined entities, collect all entities present in the retrieved nodes
    if not query_entities:
        for node in ranked_evidence:
            query_entities = query_entities.union(get_node_entities(node.content))
            
    entity_groups = {}  # entity -> modality -> list of content snippets
    fallback_nodes = []
    
    for node in ranked_evidence:
        node_ents = get_node_entities(node.content).union(get_node_entities(node.source))
        matched_ents = [ent for ent in node_ents if ent in query_entities]
        
        if matched_ents:
            for ent in matched_ents:
                if ent not in entity_groups:
                    entity_groups[ent] = {}
                modality = node.modality.upper()
                if modality not in entity_groups[ent]:
                    entity_groups[ent][modality] = []
                if node.content not in entity_groups[ent][modality]:
                    entity_groups[ent][modality].append(node.content)
        else:
            fallback_nodes.append(node)
            
    sections = []
    
    # Build entity-centric sections
    for ent in sorted(list(entity_groups.keys())):
        ent_section = [f"=== ENTITY : {ent.upper()} ==="]
        for modality in ["TEXT", "OCR", "CAPTION", "VQA", "AUDIO", "IMAGE"]:
            if modality in entity_groups[ent]:
                ent_section.append(modality)
                for item in entity_groups[ent][modality]:
                    lines = [line.strip() for line in item.split("\n") if line.strip()]
                    for line in lines:
                        if line.startswith("*") or line.startswith("-"):
                            ent_section.append(line)
                        else:
                            ent_section.append(f"* {line}")
                ent_section.append("")  # Blank line between modalities
        sections.append("\n".join(ent_section).strip())
        
    # Build general fallback section if there are any unmatched relevant nodes
    if fallback_nodes:
        fallback_section = ["=== GENERAL EVIDENCE ==="]
        fb_groups = {}
        for node in fallback_nodes:
            modality = node.modality.upper()
            fb_groups.setdefault(modality, []).append(node.content)
            
        for modality in ["TEXT", "OCR", "CAPTION", "VQA", "AUDIO", "IMAGE"]:
            if modality in fb_groups:
                fallback_section.append(modality)
                for item in fb_groups[modality]:
                    lines = [line.strip() for line in item.split("\n") if line.strip()]
                    for line in lines:
                        if line.startswith("*") or line.startswith("-"):
                            fallback_section.append(line)
                        else:
                            fallback_section.append(f"* {line}")
                fallback_section.append("")
        sections.append("\n".join(fallback_section).strip())
        
    return "\n\n".join(sections)

def _add_learning_sections(sections_list: list, learning_context: dict):
    if not learning_context:
        return
    
    # 1. Patterns
    patterns = learning_context.get("patterns", [])
    if patterns:
        pat_blocks = []
        for pat in patterns[:3]:
            supporting_ents = pat.get("supporting_entities", [])
            pat_blocks.append(f"* Sig: {pat.get('signature')} | Conf: {pat.get('confidence', 1.0):.2f} | Entities: {', '.join(supporting_ents)}")
        if pat_blocks:
            sections_list.append("=== LEARNED PATTERNS ===\n" + "\n".join(pat_blocks))

    # 2. Corrections
    corrections = learning_context.get("corrections", [])
    if corrections:
        corr_blocks = []
        for corr in corrections[:3]:
            corr_blocks.append(f"* Reason: {corr.get('reason')} | Corrected: {corr.get('corrected_answer')} | Conf: {corr.get('confidence', 1.0):.2f}")
        if corr_blocks:
            sections_list.append("=== PREVIOUS CORRECTIONS ===\n" + "\n".join(corr_blocks))

    # 3. Clusters
    clusters = learning_context.get("clusters", [])
    if clusters:
        clust_blocks = []
        for clust in clusters[:3]:
            clust_blocks.append(f"* Center: {clust.get('cluster_center_query')} | Freq: {clust.get('frequency', 1)}")
        if clust_blocks:
            sections_list.append("=== QUERY CLUSTERS ===\n" + "\n".join(clust_blocks))

    # 4. Failure History
    try:
        from app.learning.learning_store import get_failure_patterns
        failures = get_failure_patterns()
        if failures:
            fail_blocks = []
            for fail in failures[:3]:
                fail_blocks.append(f"* Type: {fail.failure_type} | Timeout count: {fail.timeout_count} | Conf: {fail.confidence:.2f}")
            if fail_blocks:
                sections_list.append("=== FAILURE HISTORY ===\n" + "\n".join(fail_blocks))
    except Exception:
        pass

def build_context(
    ranked_evidence: List[EvidenceNode],
    query: str = None,
    session_id: str = None,
    memory_nodes: List[Any] = None,
    goal: Any = None,
    plan: Any = None,
    observations: List[Any] = None,
    kg_context: dict = None,
    learning_context: dict = None
) -> str:
    """
    Constructs an entity-centric context block.
    Groups evidence snippets under standard entities and their modalities.
    If ENABLE_AGENTIC_RAG is active, it formats the prompt using Goald/Plan/Observations/Memory/Evidence structure.
    """
    from app.config import ENABLE_AGENTIC_RAG
    
    if ENABLE_AGENTIC_RAG and (goal or plan or observations):
        sections = []
        
        # 1. GOAL
        if goal:
            sections.append(f"=== GOAL ===\nGoal Type: {goal.goal_type}\nQuery: {goal.query}")
            
        # 2. PLAN
        if plan:
            steps_str = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(plan.steps)])
            sections.append(f"=== PLAN ===\n{steps_str}")
            
        # 3. RECENT OBSERVATIONS
        if observations:
            obs_str = "\n".join([f"- {obs.content}" for obs in observations])
            sections.append(f"=== RECENT OBSERVATIONS ===\n{obs_str}")
            
        # 4. RECENT MEMORY
        if memory_nodes:
            mem_blocks = []
            for m in memory_nodes[:5]:
                mem_blocks.append(f"* {m.content} [type={m.memory_type}, score={m.score:.2f}]")
            if mem_blocks:
                sections.append(f"=== RECENT MEMORY ===\n" + "\n".join(mem_blocks))
                
        # 4.5. KNOWLEDGE GRAPH
        if kg_context and kg_context.get("natural_explanation"):
            sections.append(f"=== KNOWLEDGE GRAPH ===\n{kg_context['natural_explanation']}")
            
        # 4.6. SELF-LEARNING
        _add_learning_sections(sections, learning_context)
            
        # 5. EVIDENCE CONTEXT
        if ranked_evidence:
            evidence_context = _build_evidence_context(ranked_evidence, query)
            sections.append(f"=== EVIDENCE CONTEXT ===\n{evidence_context}")
            
        # 6. SESSION SUMMARY
        if session_id:
            from app.retrieval.memory_cache import get_session_cache
            session_data = get_session_cache(session_id)
            summaries = session_data.get("summaries", [])
            if summaries:
                summary_sentences = [s.get("summary", "") for s in summaries if s.get("summary")]
                combined_summary = " ".join(summary_sentences)
                if combined_summary:
                    sections.append(f"=== SESSION SUMMARY ===\n{combined_summary}")
                    
        return "\n\n".join(sections)
        
    # Standard conversational memory layout (non-agentic fallback)
    memory_prefix_sections = []
    
    if session_id:
        from app.retrieval.session_memory import get_recent_turns
        from app.retrieval.memory_cache import get_session_cache
        
        session_data = get_session_cache(session_id)
        recent_turns = get_recent_turns(session_id, 5)
        
        # 1. Session Summary
        summaries = session_data.get("summaries", [])
        if summaries:
            summary_sentences = [s.get("summary", "") for s in summaries if s.get("summary")]
            combined_summary = " ".join(summary_sentences)
            if combined_summary:
                memory_prefix_sections.append(f"=== SESSION SUMMARY ===\n{combined_summary}")
                
        # 2. Active Entities
        active_list = session_data.get("active_entities", [])
        if active_list:
            display_names = []
            from app.retrieval.followup_resolver import ENTITY_DISPLAY_NAMES
            for ent in active_list:
                display_names.append(ENTITY_DISPLAY_NAMES.get(ent, ent.capitalize()))
            if display_names:
                memory_prefix_sections.append(f"=== ACTIVE ENTITIES ===\n" + ", ".join(display_names))
                
        # 3. Recent Conversation
        if recent_turns:
            history_blocks = []
            for idx, turn in enumerate(recent_turns):
                history_blocks.append(f"User: {turn.user_query}\nAssistant: {turn.assistant_answer}")
            memory_prefix_sections.append(f"=== RECENT CONVERSATION ===\n" + "\n\n".join(history_blocks))
 
        # 4. Retrieved Memories
        if memory_nodes:
            mem_blocks = []
            for m in memory_nodes[:5]:
                mem_blocks.append(f"* {m.content} [type={m.memory_type}, score={m.score:.2f}]")
            if mem_blocks:
                memory_prefix_sections.append(f"=== RETRIEVED MEMORIES ===\n" + "\n".join(mem_blocks))

        # 4.5. KNOWLEDGE GRAPH
        if kg_context and kg_context.get("natural_explanation"):
            memory_prefix_sections.append(f"=== KNOWLEDGE GRAPH ===\n{kg_context['natural_explanation']}")

        # 4.6. SELF-LEARNING
        _add_learning_sections(memory_prefix_sections, learning_context)

    if not ranked_evidence:
        if memory_prefix_sections:
            return "\n\n".join(memory_prefix_sections)
        return ""
        
    final_evidence_context = _build_evidence_context(ranked_evidence, query)
    if memory_prefix_sections:
        return "\n\n".join(memory_prefix_sections) + "\n\n" + final_evidence_context
    return final_evidence_context
