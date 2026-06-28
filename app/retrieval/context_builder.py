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

def _add_episodic_sections(sections_list: list, episodic_context: dict):
    from app.config import ENABLE_EPISODIC_MEMORY
    if not ENABLE_EPISODIC_MEMORY or not episodic_context:
        return
        
    # 1. EPISODIC MEMORY
    episodes = episodic_context.get("episodes", [])
    if episodes:
        blocks = []
        for ep in episodes[:5]:
            q = ep.query if hasattr(ep, "query") else ep.get("query")
            s = ep.summary if hasattr(ep, "summary") else ep.get("summary")
            blocks.append(f"* Query: {q} | Summary: {s}")
        if blocks:
            sections_list.append("=== EPISODIC MEMORY ===\n" + "\n".join(blocks))
            
    # 2. EXPERIENCE REPLAYS
    replays = episodic_context.get("replays", [])
    if replays:
        blocks = []
        for rep in replays[:5]:
            src = rep.source_episode if hasattr(rep, "source_episode") else rep.get("source_episode")
            tgt = rep.target_episode if hasattr(rep, "target_episode") else rep.get("target_episode")
            sim = rep.similarity_score if hasattr(rep, "similarity_score") else rep.get("similarity_score", 0.0)
            blocks.append(f"* Replay: source={src} target={tgt} similarity={sim:.2f}")
        if blocks:
            sections_list.append("=== EXPERIENCE REPLAYS ===\n" + "\n".join(blocks))
            
    # 3. TEMPORAL HISTORY
    chains = episodic_context.get("chains", [])
    if chains:
        blocks = []
        for ch in chains[:3]:
            ch_id = ch.chain_id if hasattr(ch, "chain_id") else ch.get("chain_id")
            eps = ch.episode_ids if hasattr(ch, "episode_ids") else ch.get("episode_ids", [])
            blocks.append(f"* Chain {ch_id}: " + " -> ".join(eps[:5]))
        if blocks:
            sections_list.append("=== TEMPORAL HISTORY ===\n" + "\n".join(blocks))
            
    # 4. MEMORY SUMMARIES
    summaries = episodic_context.get("summaries", [])
    if summaries:
        blocks = []
        for s in summaries[:3]:
            txt = s.summary_text if hasattr(s, "summary_text") else s.get("summary_text")
            blocks.append(f"* {txt}")
        if blocks:
            sections_list.append("=== MEMORY SUMMARIES ===\n" + "\n".join(blocks))

def _add_simulation_sections(sections_list: list, simulation_context: dict):
    from app.config import ENABLE_SIMULATION_ENGINE
    if not ENABLE_SIMULATION_ENGINE or not simulation_context:
        return
        
    # 1. Hypotheses
    hypotheses = simulation_context.get("hypotheses", [])
    if hypotheses:
        blocks = []
        for h in hypotheses[:3]:
            desc = h.get("description")
            conf = h.get("confidence", 1.0)
            blocks.append(f"* Description: {desc} | Confidence: {conf:.2f}")
        if blocks:
            sections_list.append("=== HYPOTHESES ===\n" + "\n".join(blocks))

    # 2. Simulations
    simulations = simulation_context.get("simulations", [])
    if simulations:
        blocks = []
        for s in simulations[:3]:
            init = s.get("initial_state")
            final = s.get("final_state")
            score = s.get("score", 0.0)
            blocks.append(f"* Path: {init} -> {final} | Score: {score:.2f}")
        if blocks:
            sections_list.append("=== SIMULATIONS ===\n" + "\n".join(blocks))

    # 3. Scenarios
    scenarios = simulation_context.get("scenarios", [])
    if scenarios:
        blocks = []
        for sc in scenarios[:3]:
            summary = sc.get("summary")
            prob = sc.get("success_probability", 1.0)
            risk = sc.get("risk_score", 0.0)
            blocks.append(f"* Scenario: {summary} | Prob: {prob:.2f} | Risk: {risk:.2f}")
        if blocks:
            sections_list.append("=== SCENARIOS ===\n" + "\n".join(blocks))

    # 4. Counterfactuals
    counterfactuals = simulation_context.get("counterfactuals", [])
    if counterfactuals:
        blocks = []
        for cf in counterfactuals[:3]:
            var = cf.get("modified_variable")
            outcome = cf.get("alternative_outcome")
            blocks.append(f"* Modified: {var} | Alternative Outcome: {outcome}")
        if blocks:
            sections_list.append("=== COUNTERFACTUALS ===\n" + "\n".join(blocks))

    # 5. Failure Forecasts
    forecasts = simulation_context.get("failure_forecasts", [])
    if forecasts:
        blocks = []
        for f in forecasts[:3]:
            ftype = f.get("failure_type")
            risk = f.get("risk_score", 0.0)
            blocks.append(f"* Failure: {ftype} | Risk: {risk:.2f}")
        if blocks:
            sections_list.append("=== FAILURE FORECASTS ===\n" + "\n".join(blocks))

def _add_meta_sections(sections_list: list, meta_context: dict):
    if not meta_context:
        return
    try:
        from app.config import (
            ENABLE_TOOL_LEARNING, ENABLE_PLANNER_POLICIES, ENABLE_STRATEGY_MEMORY,
            ENABLE_META_REFLECTION, ENABLE_POLICY_REPLAY
        )
    except ImportError:
        ENABLE_TOOL_LEARNING = True
        ENABLE_PLANNER_POLICIES = True
        ENABLE_STRATEGY_MEMORY = True
        ENABLE_META_REFLECTION = True
        ENABLE_POLICY_REPLAY = True

    # 1. TOOL LEARNING
    if ENABLE_TOOL_LEARNING:
        tools = meta_context.get("tools", [])
        if tools:
            blocks = []
            for t in tools[:3]:
                name = getattr(t, "tool_name", t.get("tool_name") if isinstance(t, dict) else "")
                success = getattr(t, "success_rate", t.get("success_rate") if isinstance(t, dict) else 1.0)
                conf = getattr(t, "confidence", t.get("confidence") if isinstance(t, dict) else 1.0)
                blocks.append(f"* Tool: {name} | Success: {success:.2f} | Conf: {conf:.2f}")
            if blocks:
                sections_list.append("=== TOOL LEARNING ===\n" + "\n".join(blocks))

    # 2. PLANNER POLICIES
    if ENABLE_PLANNER_POLICIES:
        policies = meta_context.get("policies", [])
        if policies:
            blocks = []
            for p in policies[:3]:
                p_id = getattr(p, "policy_id", p.get("policy_id") if isinstance(p, dict) else "")
                ptype = getattr(p, "planner_type", p.get("planner_type") if isinstance(p, dict) else "")
                success = getattr(p, "success_rate", p.get("success_rate") if isinstance(p, dict) else 1.0)
                conf = getattr(p, "confidence", p.get("confidence") if isinstance(p, dict) else 1.0)
                blocks.append(f"* Policy: {p_id} ({ptype}) | Success: {success:.2f} | Conf: {conf:.2f}")
            if blocks:
                sections_list.append("=== PLANNER POLICIES ===\n" + "\n".join(blocks))

    # 3. STRATEGY MEMORY
    if ENABLE_STRATEGY_MEMORY:
        strategies = meta_context.get("strategies", [])
        if strategies:
            blocks = []
            for s in strategies[:3]:
                pattern = getattr(s, "query_pattern", s.get("query_pattern") if isinstance(s, dict) else "")
                planner = getattr(s, "planner_id", s.get("planner_id") if isinstance(s, dict) else "")
                success = getattr(s, "success_rate", s.get("success_rate") if isinstance(s, dict) else 1.0)
                blocks.append(f"* Pattern: {pattern} -> Planner: {planner} | Success: {success:.2f}")
            if blocks:
                sections_list.append("=== STRATEGY MEMORY ===\n" + "\n".join(blocks))

    # 4. META REFLECTIONS
    if ENABLE_META_REFLECTION:
        reflections = meta_context.get("reflections", [])
        if reflections:
            blocks = []
            for r in reflections[:3]:
                sig = getattr(r, "query_signature", r.get("query_signature") if isinstance(r, dict) else "")
                summary = getattr(r, "reflection_summary", r.get("reflection_summary") if isinstance(r, dict) else "")
                blocks.append(f"* Ref {sig}: {summary}")
            if blocks:
                sections_list.append("=== META REFLECTIONS ===\n" + "\n".join(blocks))

    # 5. POLICY REPLAYS
    if ENABLE_POLICY_REPLAY:
        replays = meta_context.get("replays", [])
        if replays:
            blocks = []
            for rep in replays[:3]:
                src = getattr(rep, "source_policy", rep.get("source_policy") if isinstance(rep, dict) else "")
                tgt = getattr(rep, "target_policy", rep.get("target_policy") if isinstance(rep, dict) else "")
                sim = getattr(rep, "similarity", rep.get("similarity") if isinstance(rep, dict) else 1.0)
                blocks.append(f"* Replay: {src} -> {tgt} | Similarity: {sim:.2f}")
            if blocks:
                sections_list.append("=== POLICY REPLAYS ===\n" + "\n".join(blocks))

def _add_personality_sections(sections_list: list, personality_context: dict):
    from app.config import ENABLE_HUMAN_PREFERENCES
    if not ENABLE_HUMAN_PREFERENCES or not personality_context:
        return
        
    # 1. Human Preferences
    prefs = personality_context.get("preferences", [])
    if prefs:
        blocks = []
        for p in prefs[:3]:
            depth = getattr(p, "explanation_depth", p.get("explanation_depth", "medium") if isinstance(p, dict) else "medium")
            tone = getattr(p, "tone_preference", p.get("tone_preference", "professional") if isinstance(p, dict) else "professional")
            length = getattr(p, "response_length", p.get("response_length", 200) if isinstance(p, dict) else 200)
            blocks.append(f"* Tone: {tone} | Depth: {depth} | Length: {length} chars")
        if blocks:
            sections_list.append("=== HUMAN PREFERENCES ===\n" + "\n".join(blocks))

    # 2. Personality Profile
    p_type = personality_context.get("selected_personality")
    patterns = personality_context.get("speaking_patterns", [])
    exp_prefs = personality_context.get("explanation_preferences", [])
    if p_type:
        pers_block = [f"Selected Personality Type: {p_type}"]
        if patterns:
            pers_block.append("Speaking Patterns:")
            for pat in patterns[:3]:
                pers_block.append(f"- {pat}")
        if exp_prefs:
            pers_block.append("Explanation Preferences:")
            for exp in exp_prefs[:3]:
                pers_block.append(f"- {exp}")
        sections_list.append("=== ADAPTIVE PERSONALITY PROFILING ===\n" + "\n".join(pers_block))

def build_context(
    ranked_evidence: List[EvidenceNode],
    query: str = None,
    session_id: str = None,
    memory_nodes: List[Any] = None,
    goal: Any = None,
    plan: Any = None,
    observations: List[Any] = None,
    kg_context: dict = None,
    learning_context: dict = None,
    episodic_context: dict = None,
    simulation_context: dict = None,
    meta_context: dict = None,
    personality_context: dict = None
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
        
        # 4.7. EPISODIC MEMORY
        _add_episodic_sections(sections, episodic_context)

        # 4.8. SIMULATION CONTEXT
        _add_simulation_sections(sections, simulation_context)

        # 4.9. META COGNITION
        _add_meta_sections(sections, meta_context)
        
        # 4.10. ADAPTIVE PERSONALITY & PREFERENCES
        _add_personality_sections(sections, personality_context)
            
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
        
        # 4.7. EPISODIC MEMORY
        _add_episodic_sections(memory_prefix_sections, episodic_context)

        # 4.8. SIMULATION CONTEXT
        _add_simulation_sections(memory_prefix_sections, simulation_context)

        # 4.9. META COGNITION
        _add_meta_sections(memory_prefix_sections, meta_context)
        
        # 4.10. ADAPTIVE PERSONALITY & PREFERENCES
        _add_personality_sections(memory_prefix_sections, personality_context)

    if not ranked_evidence:
        if memory_prefix_sections:
            return "\n\n".join(memory_prefix_sections)
        return ""
        
    final_evidence_context = _build_evidence_context(ranked_evidence, query)
    if memory_prefix_sections:
        return "\n\n".join(memory_prefix_sections) + "\n\n" + final_evidence_context
    return final_evidence_context


