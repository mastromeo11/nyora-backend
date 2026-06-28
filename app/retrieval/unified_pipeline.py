import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.llm.ollama_client import ollama_client
from app.retrieval.unified_retriever import retrieve_evidence
from app.retrieval.evidence_ranker import rank_evidence
from app.retrieval.relevance_filter import filter_irrelevant_nodes
from app.retrieval.entity_consensus_engine import aggregate_entity_consensus
from app.retrieval.evidence_compressor import compress_evidence
from app.retrieval.consensus_engine import evaluate_consensus
from app.retrieval.context_builder import build_context, get_node_entities
from app.retrieval.citation_engine import generate_citations
from app.retrieval.explanation_engine import generate_why_this_answer
from app.retrieval.grounding_validator import validate_grounding

from app.retrieval.memory_models import ConversationTurn
from app.retrieval.followup_resolver import resolve_followup
from app.retrieval.preference_memory import update_preferences_from_query
from app.retrieval.memory_retriever import retrieve_memories
from app.retrieval.memory_ranker import rank_memory_nodes
from app.retrieval.importance_engine import calculate_importance
from app.retrieval.entity_memory_engine import update_entity_memories
from app.retrieval.active_entity_tracker import track_active_entities
from app.retrieval.memory_compressor import compress_older_turns
from app.retrieval.session_memory import add_turn
from app.retrieval.memory_explanation_engine import compile_memory_diagnostics
from app.retrieval.conversation_summarizer import summarize_session_if_needed
from app.retrieval.memory_metrics import increment_query, increment_hit, increment_cache_hit, record_latency, get_total_queries

# Configuration imports
from app.config import (
    ENABLE_MEMORY, ENABLE_AGENTIC_RAG, ENABLE_TRACE_CACHE, ENABLE_AGENT_EXPLANATIONS,
    ENABLE_KNOWLEDGE_GRAPH, ENABLE_TEMPORAL_EDGES, GRAPH_PRUNE_INTERVAL,
    ENABLE_SELF_LEARNING, ENABLE_PATTERN_PRUNER, PATTERN_PRUNE_INTERVAL,
    ENABLE_EPISODIC_MEMORY, ENABLE_SIMULATION_ENGINE,
    ENABLE_TOOL_LEARNING, ENABLE_META_REFLECTION, ENABLE_PLANNER_POLICIES,
    ENABLE_POLICY_REPLAY, ENABLE_STRATEGY_MEMORY, ENABLE_POLICY_COMPRESSION,
    ENABLE_POLICY_REINFORCEMENT, ENABLE_TOOL_FAILURE_TRACKING, ENABLE_META_EXPLANATIONS,
    ENABLE_POLICY_DECAY, ENABLE_POLICY_PRUNER, ENABLE_POLICY_CACHE,
    ENABLE_POLICY_MIGRATIONS, ENABLE_POLICY_ARCHIVES, ENABLE_POLICY_SIMILARITY_CACHE,
    ENABLE_CONFIDENCE_CALIBRATION, ENABLE_FAILURE_GRAPH_ISOLATION,
    ENABLE_HUMAN_PREFERENCES
)

# Knowledge Graph imports
from app.retrieval.knowledge_retriever import retrieve_knowledge
from app.retrieval.entity_extractor import extract_entities_from_text, build_or_update_entity_node
from app.retrieval.relation_extractor import extract_relations_from_text
from app.retrieval.community_detector import detect_communities
from app.retrieval.relation_decay_engine import decay_graph
from app.retrieval.graph_pruner import prune_graph
from app.retrieval.graph_store import append_entities, append_relations, append_temporal_event, get_entities
from app.retrieval.knowledge_models import TemporalNode
from app.retrieval.entity_alias_registry import normalize_entity_name

# Continual Learning imports
from app.learning.learning_retriever import retrieve_learning_context
from app.learning.feedback_engine import compile_and_store_feedback
from app.learning.pattern_engine import compile_and_store_pattern
from app.learning.correction_engine import compile_and_store_correction
from app.learning.failure_pattern_engine import compile_and_store_failure_pattern
from app.learning.query_cluster_engine import cluster_query
from app.learning.active_learning_engine import evaluate_active_learning
from app.learning.pattern_decay_engine import decay_learning_memory
from app.learning.pattern_pruner import prune_learning_memory
from app.learning.learning_store import get_patterns, get_corrections, get_feedback, get_clusters, get_failure_patterns

# Agentic RAG module imports
from app.retrieval.goal_detector import classify_and_detect_goal
from app.retrieval.task_decomposer import decompose_goal
from app.retrieval.planner import generate_plan
from app.retrieval.react_engine import run_react_reasoning
from app.retrieval.trace_cache import get_cached_trace, save_trace
from app.retrieval.observation_memory import store_observations, retrieve_cached_observations
from app.retrieval.task_memory import save_task_execution, get_cached_tasks
from app.retrieval.agent_graph import build_agent_graph
from app.retrieval.agent_ranker import rank_agent_traces
from app.retrieval.agent_explanation_engine import generate_agent_explanation

# Thread-safe global store for debug endpoints
_latest_entities_debug = {}
_latest_agent_debug = {
    "goal": None,
    "plan": None,
    "tasks": [],
    "executed_tools": [],
    "observations": [],
    "reflections": [],
    "trace": None
}

def get_latest_entities_debug() -> dict:
    return _latest_entities_debug

def get_latest_agent_debug() -> dict:
    return _latest_agent_debug

def reset_latest_agent_debug():
    global _latest_agent_debug
    _latest_agent_debug = {
        "goal": None,
        "plan": None,
        "tasks": [],
        "executed_tools": [],
        "observations": [],
        "reflections": [],
        "trace": None
    }
    from app.retrieval.replanner import reset_replanner_count
    reset_replanner_count()

def update_knowledge_graph(
    query: str,
    final_answer: str,
    session_id: str,
    filtered_evidence: List[Any],
    goal: Any = None,
    plan: Any = None,
    tasks: List[Any] = None,
    executed_tools: List[Any] = None,
    observations: List[Any] = None,
    reflections: List[Any] = None,
    trace_dict: Any = None
):
    if not ENABLE_KNOWLEDGE_GRAPH:
        return
        
    try:
        # 1. Extract entities and relations from retrieved evidence
        extracted_entities = []
        extracted_relations = []
        
        now_str = datetime.utcnow().isoformat()
        
        # Keep track of existing entities to get current mentions/metadata
        existing_entities = {ent.canonical_name: ent for ent in get_entities()}
        
        # Helper to register an entity node
        registered_canonicals = set()
        def register_entity(name: str):
            canonical = normalize_entity_name(name)
            if canonical in registered_canonicals:
                return
            registered_canonicals.add(canonical)
            
            existing = existing_entities.get(canonical)
            ent_node = build_or_update_entity_node(
                existing_node=existing,
                name=name,
                entity_type="conceptual",
                source="pipeline_turn",
                modality="text",
                confidence=1.0
            )
            extracted_entities.append(ent_node)
            
        for node in filtered_evidence:
            if isinstance(node, dict):
                content = node.get("content", "")
                source = node.get("source", "unknown")
                modality = node.get("modality", "text")
                evidence_id = node.get("evidence_id", None)
            else:
                content = getattr(node, "content", "")
                source = getattr(node, "source", "unknown")
                modality = getattr(node, "modality", "text")
                evidence_id = getattr(node, "evidence_id", None)
            
            # Extract entities from evidence text
            ents = extract_entities_from_text(content)
            for ent in ents:
                register_entity(ent)
                
            # Extract relations from evidence text
            rels = extract_relations_from_text(
                content,
                evidence_ids=[evidence_id] if evidence_id else [],
                source_modalities=[modality] if modality else [],
                created_by="evidence_ingestion"
            )
            extracted_relations.extend(rels)
            
        # 2. Extract relations from QA (query + answer)
        qa_text = query + " " + final_answer
        ents_qa = extract_entities_from_text(qa_text)
        for ent in ents_qa:
            register_entity(ent)
            
        rels_qa = extract_relations_from_text(
            qa_text,
            evidence_ids=[],
            source_modalities=["text"],
            created_by="qa_interaction"
        )
        extracted_relations.extend(rels_qa)
        
        # 3. Handle agentic nodes extraction if agent flow was used
        if goal:
            g_query = goal.get("query") if isinstance(goal, dict) else getattr(goal, "query", "")
            for ent in extract_entities_from_text(g_query or ""):
                register_entity(ent)
        if tasks:
            for task in tasks:
                t_desc = task.get("description") if isinstance(task, dict) else getattr(task, "description", "")
                for ent in extract_entities_from_text(t_desc or ""):
                    register_entity(ent)
        if observations:
            for obs in observations:
                o_content = obs.get("content") if isinstance(obs, dict) else getattr(obs, "content", "")
                for ent in extract_entities_from_text(o_content or ""):
                    register_entity(ent)
        if reflections:
            for refl in reflections:
                r_reason = refl.get("reason") if isinstance(refl, dict) else getattr(refl, "reason", "")
                for ent in extract_entities_from_text(r_reason or ""):
                    register_entity(ent)

        # 4. Temporal node compilation if ENABLE_TEMPORAL_EDGES is True
        if ENABLE_TEMPORAL_EDGES:
            # Create a temporal node summarizing this turn
            event_id = f"evt_{uuid.uuid4().hex[:8]}"
            description = f"Turn interaction on query: '{query[:50]}...'"
            # Collect canonical entity names mentioned in this turn
            entities_in_turn = list(ents_qa)
            
            t_node = TemporalNode(
                event_id=event_id,
                description=description,
                timestamp=datetime.utcnow().isoformat(),
                entities=entities_in_turn,
                event_type="query_turn",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                last_seen=datetime.utcnow().isoformat()
            )
            append_temporal_event(t_node)
            
        # 5. Append all entities and relations
        if extracted_entities:
            append_entities(extracted_entities)
        if extracted_relations:
            append_relations(extracted_relations)
            
        # 6. Run Community Detection to update community mappings & node centralities
        detect_communities()
        
        # 7. Check decay & pruning interval
        total_queries = get_total_queries()
        if total_queries > 0 and total_queries % GRAPH_PRUNE_INTERVAL == 0:
            print(f"[KG PIPELINE] Running decay and pruning cycle at query count: {total_queries}")
            decay_graph()
            prune_graph()
            
    except Exception as e:
        print(f"[KG PIPELINE] Error updating knowledge graph: {e}")

def is_meta_query(query: str) -> bool:
    q = query.lower()
    meta_keywords = [
        "summarize our discussion",
        "summarize the discussion",
        "summarize our conversation",
        "summarize the conversation",
        "summarize discussion",
        "summarize conversation",
        "summarize our chat",
        "summarize the chat",
        "summarize what we",
        "what did we discuss",
        "what was discussed",
        "what we discussed",
        "our discussion",
        "our conversation",
        "my preference",
        "user preference",
        "what preferences",
        "model preferences",
        "what did i ask",
        "what did i say"
    ]
    return any(kw in q for kw in meta_keywords)

def answer_query(query: str, session_id: str = "default_session") -> dict:
    """
    Orchestrates execution of the RAG pipeline.
    Enforces the structured sequence:
    Memory -> Learning -> Episodes -> Experience Replay -> World State Builder -> Simulation Engine -> Policy Simulation -> Branch Ranking -> Planner -> Swarm -> Retrieval -> Grounding
    """
    # Run privacy filter firewall
    from app.personality.privacy_filter_engine import filter_sensitive_info
    query, was_filtered = filter_sensitive_info(query)

    # Route execution to Swarm Coordinator if enabled
    from app.config import ENABLE_MULTI_AGENT_SWARM
    if ENABLE_MULTI_AGENT_SWARM:
        from app.swarm.swarm_manager import swarm_manager
        return swarm_manager.execute_swarm_query(query)

    # Check if Agentic RAG is enabled
    if ENABLE_AGENTIC_RAG:
        t_agent_start = time.time()
        
        # 1. Resolve pronouns in query using history (fast resolved query)
        resolved_query = resolve_followup(query, session_id) if ENABLE_MEMORY else query
        
        # Get personality context
        personality_context = None
        selected_personality = "concise engineer"
        if ENABLE_HUMAN_PREFERENCES:
            try:
                from app.personality.personality_retriever import get_relevant_preferences
                from app.personality.personality_optimizer import select_adaptive_personality
                from app.personality.adaptive_personality_engine import get_or_create_personality
                
                relevant_prefs = [p[0] for p in get_relevant_preferences(resolved_query)]
                selected_personality = select_adaptive_personality(resolved_query)
                pers_node = get_or_create_personality(selected_personality)
                
                personality_context = {
                    "preferences": relevant_prefs,
                    "selected_personality": selected_personality,
                    "speaking_patterns": pers_node.speaking_patterns if pers_node else [],
                    "explanation_preferences": pers_node.explanation_preferences if pers_node else []
                }
            except Exception as e:
                print(f"[PIPELINE PERSONALITY] Error: {e}")
        
        # 2. Check Trace Cache (Step 12) for repeated queries
        cached_trace = get_cached_trace(session_id, resolved_query) if ENABLE_TRACE_CACHE else None
        
        if cached_trace:
            print(f"[AGENT PIPELINE] Trace cache hit! Reusing plan: {cached_trace['plan_id']}")
            # Retrieve completed tasks and outputs from task memory
            cached_execution = get_cached_tasks(session_id, resolved_query)
            if cached_execution:
                tasks = cached_execution["tasks"]
                results = cached_execution["results"]
                
                # Directly unpack and return results
                _latest_agent_debug = {
                    "goal": cached_trace.get("goal"),
                    "plan": cached_trace.get("plan") or cached_trace,
                    "tasks": tasks,
                    "executed_tools": cached_execution.get("executed_tools", []),
                    "observations": cached_execution.get("observations", []),
                    "reflections": cached_execution.get("reflections", []),
                    "trace": cached_trace
                }
                # Return standard formatted response payload
                return results
                
        # Simulation, Hypothesis & Scenario Generation
        simulation_context = None
        current_state = None
        if ENABLE_SIMULATION_ENGINE:
            try:
                from app.simulation.simulation_retriever import retrieve_simulation_context
                from app.simulation.hypothesis_engine import generate_hypothesis
                from app.simulation.scenario_generator import generate_scenario_branch
                from app.simulation.world_state_compressor import compress_current_world_state
                
                simulation_context = retrieve_simulation_context(resolved_query)
                
                if "what if" in resolved_query.lower() or "suppose" in resolved_query.lower() or "if" in resolved_query.lower():
                    generate_hypothesis(
                        description=resolved_query,
                        supporting_entities=[]
                    )
                
                current_state = compress_current_world_state()
                generate_scenario_branch(
                    parent_state_id=current_state.world_state_id,
                    summary=f"Simulated execution path for query: {resolved_query[:40]}...",
                    success_probability=0.9,
                    risk_score=0.1,
                    importance_score=0.7
                )
            except Exception as e:
                print(f"[PIPELINE SIMULATION] Error in pre-execution simulation: {e}")

        # Policy Replay & Planner Optimizer
        selected_planner = "ReAct"
        replays = []
        if ENABLE_POLICY_REPLAY:
            try:
                from app.meta.policy_replay_engine import get_replays_ranked
                replays = get_replays_ranked(resolved_query)
            except Exception as e:
                print(f"[PIPELINE META] Error getting replays: {e}")
                
        if ENABLE_PLANNER_POLICIES:
            try:
                from app.meta.planner_optimizer import select_planner
                selected_planner = select_planner(resolved_query)
                print(f"[PIPELINE META] Optimizer selected planner: {selected_planner}")
            except Exception as e:
                print(f"[PIPELINE META] Error optimizing planner: {e}")

        # 3. Goal Detection
        goal_node = classify_and_detect_goal(resolved_query)
        
        # 4. Task Decomposition
        tasks = decompose_goal(goal_node)
        
        # 5. Planning
        plan_node = generate_plan(goal_node, tasks)
        
        # 6. Retrieve and rank memory nodes (pre-fetch for agent context)
        memory_nodes = []
        if ENABLE_MEMORY:
            # Update preference tracking
            update_preferences_from_query(session_id, resolved_query)
            memory_nodes = retrieve_memories(session_id)
            memory_nodes = rank_memory_nodes(memory_nodes, resolved_query)
            
        # 7. Execute ReAct Loop (Thought -> Action -> Observation)
        executed_tools, observations, reflections, collected_evidence = run_react_reasoning(
            goal=goal_node,
            plan=plan_node,
            tasks=tasks,
            session_id=session_id
        )
        
        # If no evidence was retrieved during ReAct loop, fallback to normal retrieval
        if not collected_evidence:
            print("[AGENT PIPELINE] ReAct loop retrieved no evidence. Falling back to default retriever search.")
            collected_evidence = retrieve_evidence(resolved_query)
            
        # 8. Rank and filter evidence nodes
        ranked_evidence = rank_evidence(collected_evidence, resolved_query)
        filtered_evidence = filter_irrelevant_nodes(resolved_query, ranked_evidence)
        
        # 9. Evaluate consensus
        entity_consensus = aggregate_entity_consensus(filtered_evidence)
        consensus_score, supporting_modalities = evaluate_consensus(filtered_evidence)
        
        # Group and log entities debug
        entities_debug = {}
        for c_node in entity_consensus:
            srcs = {node.source for node in filtered_evidence if c_node.entity in get_node_entities(node.content).union(get_node_entities(node.source))}
            ent_consensus_score = min(0.40 + c_node.consensus_score, 1.0)
            entities_debug[c_node.entity] = {
                "modalities": c_node.modalities,
                "sources": sorted(list(srcs)),
                "consensus_score": round(ent_consensus_score, 4)
            }
        _latest_entities_debug = entities_debug
        
        # Compress evidence nodes for builder
        compressed_evidence = compress_evidence(filtered_evidence)
        
        # Retrieve Knowledge Graph context
        kg_context = None
        if ENABLE_KNOWLEDGE_GRAPH:
            kg_context = retrieve_knowledge(resolved_query, session_id)
            
        # Retrieve Continual Learning context
        learning_context = None
        if ENABLE_SELF_LEARNING:
            learning_context = retrieve_learning_context(resolved_query)
            
        # Retrieve Episodic Memory context
        episodic_context = None
        if ENABLE_EPISODIC_MEMORY:
            from app.episodic.episodic_retriever import retrieve_episodic_context
            episodic_context = retrieve_episodic_context(resolved_query)
            
        # Retrieve Simulation context
        if ENABLE_SIMULATION_ENGINE and simulation_context is None:
            from app.simulation.simulation_retriever import retrieve_simulation_context
            simulation_context = retrieve_simulation_context(resolved_query)
            
        # Retrieve Meta context
        meta_context = None
        if ENABLE_PLANNER_POLICIES or ENABLE_TOOL_LEARNING:
            try:
                from app.meta.meta_retriever import retrieve_meta_context
                meta_context = retrieve_meta_context(resolved_query)
            except Exception as e:
                print(f"[PIPELINE META] Error retrieving meta context: {e}")

        # 10. Context Builder (Incorporate goal details, plans, observations, and contexts)
        context = build_context(
            ranked_evidence=compressed_evidence,
            query=resolved_query,
            session_id=session_id if ENABLE_MEMORY else None,
            memory_nodes=memory_nodes,
            goal=goal_node,
            plan=plan_node,
            observations=observations,
            kg_context=kg_context,
            learning_context=learning_context,
            episodic_context=episodic_context,
            simulation_context=simulation_context,
            meta_context=meta_context,
            personality_context=personality_context
        )
        
        # 11. LLM Generation
        llm_query = resolved_query
        for flag in ["(simulate_failure)", "simulate_failure"]:
            llm_query = llm_query.replace(flag, "")
        llm_query = llm_query.strip()
        raw_answer = ollama_client.generate_response(query=llm_query, context=context)
        
        # 12. Grounding Validator (Authoritative source of truth)
        if ENABLE_MEMORY and (is_meta_query(query) or is_meta_query(resolved_query)):
            final_answer = raw_answer
            grounding_report = [{"claim": "Bypassed for meta-query", "status": "Supported"}]
        else:
            final_answer, grounding_report = validate_grounding(raw_answer, filtered_evidence, observations, reflections)
            
        # 13. Compile structured citations and explanations
        citations = generate_citations(filtered_evidence)
        why_this_answer = generate_why_this_answer(filtered_evidence)
        
        # Score trace using ranker
        trace_score = rank_agent_traces(observations, tasks, memory_nodes, filtered_evidence)
        confidence_label = "High" if trace_score >= 0.70 else ("Medium" if trace_score >= 0.45 else "Low")
        
        # Compile response payload
        response = {
            "answer": final_answer,
            "confidence": confidence_label,
            "confidence_score": trace_score,
            "sources": citations,
            "evidence": [node.dict() for node in filtered_evidence],
            "why_this_answer": why_this_answer,
            "supporting_modalities": supporting_modalities,
            "goal": goal_node.dict(),
            "plan": plan_node.dict(),
            "observations": [o.dict() for o in observations],
            "reflections": [r.dict() for r in reflections],
            "debug_details": {
                "query": query,
                "resolved_query": resolved_query,
                "raw_answer": raw_answer,
                "grounding_report": grounding_report,
                "consensus_score": consensus_score,
                "compressed_context_size": len(context)
            }
        }
        
        # 14. Explainability compilation without raw chain-of-thought leakage
        if ENABLE_AGENT_EXPLANATIONS:
            agent_expl = generate_agent_explanation(
                goal_node, plan_node, executed_tools, observations, reflections, citations
            )
            if ENABLE_HUMAN_PREFERENCES:
                try:
                    from app.personality.personality_explanation_engine import compile_personality_explanation
                    pers_expl = compile_personality_explanation(
                        preference_applied=True,
                        personality_type=selected_personality
                    )
                    if pers_expl:
                        agent_expl = pers_expl + "\n" + agent_expl
                except Exception as e:
                    print(f"[PIPELINE PERSONALITY] Error compiling explanation: {e}")
            if ENABLE_META_EXPLANATIONS:
                try:
                    from app.meta.meta_explanation_engine import compile_meta_explanation
                    from app.meta.meta_store import get_policies
                    meta_expl = compile_meta_explanation(replays, get_policies())
                    if meta_expl:
                        agent_expl = meta_expl + "\n" + agent_expl
                except Exception as e:
                    print(f"[PIPELINE META] Explanation compilation error: {e}")
            if ENABLE_EPISODIC_MEMORY and episodic_context:
                from app.episodic.episodic_explanation_engine import compile_episodic_explanation
                epis_expl = compile_episodic_explanation(episodic_context.get("replays", []))
                if epis_expl:
                    agent_expl = epis_expl + "\n" + agent_expl
            response["explanation"] = agent_expl
            
        # Evolve long-term episodic memory
        if ENABLE_EPISODIC_MEMORY:
            try:
                from app.episodic.episode_builder import build_and_store_episode
                from app.episodic.temporal_memory_engine import update_temporal_chains
                from app.episodic.episode_cluster_engine import cluster_episode
                from app.episodic.experience_replay_engine import record_replay
                from app.episodic.memory_decay_engine import decay_episodic_memory
                from app.episodic.memory_pruner import prune_episodic_memory
                from app.config import ENABLE_MEMORY_DECAY, ENABLE_MEMORY_PRUNER, EPISODE_PRUNE_INTERVAL
                
                success = (len(reflections) == 0) or ("not available" not in final_answer.lower())
                
                ep_node, exp_node = build_and_store_episode(
                    query=query,
                    answer=final_answer,
                    confidence_label_or_score=trace_score,
                    grounding_report=grounding_report,
                    user_signal=1.0,
                    experience_type="agentic_rag",
                    supporting_evidence_ids=[getattr(n, "evidence_id", None) or n.get("evidence_id") for n in filtered_evidence if (getattr(n, "evidence_id", None) or n.get("evidence_id"))],
                    planner_trace_ids=[plan_node.plan_id] if plan_node else [],
                    tools_used=executed_tools,
                    observation_ids=[getattr(o, "observation_id", None) or o.get("observation_id") for o in observations if (getattr(o, "observation_id", None) or o.get("observation_id"))],
                    reflection_ids=[getattr(r, "reflection_id", None) or r.get("reflection_id") for r in reflections if (getattr(r, "reflection_id", None) or r.get("reflection_id"))],
                    success_status=success,
                    execution_latency=(time.time() - t_agent_start) * 1000.0
                )
                
                if ep_node:
                    update_temporal_chains(ep_node)
                    cluster_episode(ep_node)
                    
                    # Record reinforcement replays
                    for old_ep in episodic_context.get("episodes", []):
                        record_replay(old_ep.episode_id, ep_node.episode_id, 0.9, 1.0)
                        
                if ENABLE_MEMORY_DECAY:
                    decay_episodic_memory()
                    
                if ENABLE_MEMORY_PRUNER and get_total_queries() > 0 and get_total_queries() % EPISODE_PRUNE_INTERVAL == 0:
                    prune_episodic_memory()
            except Exception as e:
                print(f"[PIPELINE EPISODIC] Error during episodic memory storage: {e}")
            
        # Simulation explainability integration
        if ENABLE_SIMULATION_ENGINE and ENABLE_AGENT_EXPLANATIONS:
            try:
                from app.simulation.simulation_explanation_engine import compile_simulation_explanation
                from app.simulation.simulation_store import get_scenarios, get_failure_forecasts
                sim_expl = compile_simulation_explanation(get_scenarios(), get_failure_forecasts())
                if sim_expl:
                    response["explanation"] = sim_expl + "\n" + response.get("explanation", "")
            except Exception as e:
                print(f"[PIPELINE SIMULATION] Error generating explanation: {e}")

        # Simulation database updates, decay, and pruner
        if ENABLE_SIMULATION_ENGINE:
            try:
                from app.simulation.simulation_engine import record_simulation_run
                from app.simulation.simulation_decay_engine import decay_simulation_memory
                from app.simulation.simulation_pruner import prune_simulation_memory
                from app.config import SIMULATION_PRUNE_INTERVAL
                
                success_status = (len(reflections) == 0) or ("not available" not in final_answer.lower())
                score = 1.0 if success_status else 0.0
                
                initial_state_id = current_state.world_state_id if current_state else "ws_init"
                final_state_id = f"ws_final_{uuid.uuid4().hex[:8]}"
                
                record_simulation_run(
                    initial_state_id=initial_state_id,
                    final_state_id=final_state_id,
                    scenario_chain=[],
                    score=score,
                    planner_trace_ids=[plan_node.plan_id] if plan_node else [],
                    agent_ids=["planner"],
                    tool_ids=executed_tools
                )
                
                decay_simulation_memory()
                
                tq = get_total_queries()
                if tq > 0 and tq % SIMULATION_PRUNE_INTERVAL == 0:
                    prune_simulation_memory()
            except Exception as e:
                print(f"[PIPELINE SIMULATION] Error in post-execution updates: {e}")
            
        # Update trace cache & memory nodes
        success = (len(reflections) == 0) or ("not available" not in final_answer.lower())
        trace_dict = {
            "trace_id": f"trace_{uuid.uuid4().hex[:8]}",
            "goal_id": goal_node.goal_id,
            "plan_id": plan_node.plan_id,
            "steps": plan_node.steps,
            "success": success
        }
        
        if ENABLE_TRACE_CACHE and success:
            goal_dict = goal_node.dict() if hasattr(goal_node, "dict") else goal_node
            plan_dict = plan_node.dict() if hasattr(plan_node, "dict") else plan_node
            save_trace(session_id, resolved_query, goal_dict, plan_dict, success)
            save_task_execution(session_id, resolved_query, tasks, response, executed_tools, observations, reflections)
            
        if ENABLE_MEMORY:
            # Create turn Node
            importance_score = calculate_importance(query, final_answer, citations, trace_score)
            if importance_score >= 0.3:
                turn = ConversationTurn(
                    turn_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_query=query,
                    assistant_answer=final_answer,
                    timestamp=datetime.utcnow().isoformat(),
                    retrieved_sources=[c["source"] for c in citations],
                    entities=list(get_node_entities(resolved_query).union(get_node_entities(final_answer))),
                    intent_profile="",
                    confidence=confidence_label
                )
                add_turn(session_id, turn)
                update_entity_memories(session_id, resolved_query, final_answer, [c["source"] for c in citations], supporting_modalities, trace_score)
                track_active_entities(session_id, resolved_query, final_answer)
                compress_older_turns(session_id)
                summarize_session_if_needed(session_id)
                
            # Storing observations with decay rules
            store_observations(session_id, observations)
            
        # Update semantic graph representation
        build_agent_graph(filtered_evidence, session_id, goal_node, plan_node, tasks, executed_tools, observations, reflections, trace_dict)
        
        # Evolve knowledge graph with current turn data
        update_knowledge_graph(
            query=query,
            final_answer=final_answer,
            session_id=session_id,
            filtered_evidence=filtered_evidence,
            goal=goal_node,
            plan=plan_node,
            tasks=tasks,
            executed_tools=executed_tools,
            observations=observations,
            reflections=reflections,
            trace_dict=trace_dict
        )
        
        # Update self-learning layer
        if ENABLE_SELF_LEARNING:
            try:
                has_refutations = False
                if grounding_report:
                    has_refutations = any(str(item.get("status", "")).lower() == "refuted" for item in grounding_report)
                
                success_agent = ((len(reflections) == 0) or ("not available" not in final_answer.lower())) and not has_refutations
                
                feedback_type = "SUCCESS"
                if not success_agent:
                    feedback_type = "CORRECTION" if has_refutations else "FAILURE"
                elif confidence_label.lower() == "low":
                    feedback_type = "LOW_CONFIDENCE"
                    
                compile_and_store_feedback(
                    query=query,
                    answer=final_answer,
                    feedback_type=feedback_type,
                    confidence_label=confidence_label,
                    grounding_report=grounding_report
                )
                
                evidence_ids = []
                source_modalities = []
                for node in filtered_evidence:
                    if isinstance(node, dict):
                        ev_id = node.get("evidence_id") or node.get("id")
                        mod = node.get("modality") or "text"
                    else:
                        ev_id = getattr(node, "evidence_id", None) or getattr(node, "id", None)
                        mod = getattr(node, "modality", "text")
                    if ev_id:
                        evidence_ids.append(str(ev_id))
                    if mod:
                        source_modalities.append(str(mod))
                        
                compile_and_store_pattern(
                    query=resolved_query,
                    entity_set=get_node_entities(resolved_query),
                    intent_type=goal_node.goal_type if goal_node else "general",
                    success=success_agent,
                    evidence_ids=evidence_ids,
                    source_modalities=source_modalities
                )
                
                evaluate_active_learning(
                    query=resolved_query,
                    answer=final_answer,
                    confidence_label=confidence_label,
                    grounding_report=grounding_report,
                    executed_tools=executed_tools,
                    reflections=reflections
                )
                
                if reflections:
                    refl_ids = []
                    refl_reasons = []
                    for r in reflections:
                        if isinstance(r, dict):
                            refl_ids.append(r.get("reflection_id") or "")
                            refl_reasons.append(r.get("reason") or "")
                        else:
                            refl_ids.append(getattr(r, "reflection_id", ""))
                            refl_reasons.append(getattr(r, "reason", ""))
                    refl_ids = [rid for rid in refl_ids if rid]
                    refl_reasons_str = "; ".join([r for r in refl_reasons if r])
                    compile_and_store_correction(
                        reason=f"Reflection trigger: {refl_reasons_str}" if refl_reasons_str else "Reflection trigger",
                        original_answer=raw_answer,
                        corrected_answer=final_answer,
                        reflection_ids=refl_ids,
                        source="reflection_engine"
                    )
                
                cluster_query(query=resolved_query, success=success_agent)
                
                total_queries = get_total_queries()
                if total_queries > 0 and total_queries % PATTERN_PRUNE_INTERVAL == 0:
                    decay_learning_memory()
                    prune_learning_memory()
            except Exception as e:
                print(f"[LEARNING PIPELINE] Error updating self-learning: {e}")
        # Meta-Cognition updates
        success_turn = (len(reflections) == 0) and ("not available" not in final_answer.lower())
        
        if ENABLE_META_REFLECTION:
            try:
                from app.meta.meta_reflection_engine import generate_meta_reflection
                generate_meta_reflection(
                    query=query,
                    success=success_turn,
                    tool_sequence=executed_tools,
                    latency_ms=(time.time() - t_agent_start) * 1000.0,
                    plan_steps=len(tasks),
                    evidence_count=len(filtered_evidence)
                )
            except Exception as e:
                print(f"[PIPELINE META] Error in meta reflection: {e}")
                
        if ENABLE_TOOL_LEARNING:
            try:
                from app.meta.tool_learning_engine import record_tool_execution
                from app.meta.tool_failure_engine import record_tool_failure
                for tool in executed_tools:
                    record_tool_execution(
                        tool_name=tool,
                        success=success_turn,
                        latency_ms=150.0,
                        confidence=trace_score if 'trace_score' in locals() else 1.0
                    )
                    if not success_turn:
                        record_tool_failure(tool_name=tool, failure_type="pipeline_outcome_failure")
            except Exception as e:
                print(f"[PIPELINE META] Error in tool learning update: {e}")
                
        if ENABLE_PLANNER_POLICIES:
            try:
                from app.meta.planner_policy_engine import record_policy_run
                from app.meta.policy_failure_engine import record_policy_failure
                policy_id = plan_node.plan_id if plan_node else f"pol_{uuid.uuid4().hex[:8]}"
                record_policy_run(
                    policy_id=policy_id,
                    planner_type=selected_planner,
                    tool_sequence=executed_tools,
                    intent_type=goal_node.goal_type if goal_node else "general",
                    entities=list(get_node_entities(resolved_query)),
                    success=success_turn,
                    latency_ms=(time.time() - t_agent_start) * 1000.0,
                    confidence=trace_score if 'trace_score' in locals() else 1.0
                )
                if not success_turn:
                    record_policy_failure(policy_id=policy_id, failure_reason="pipeline_outcome_failure")
            except Exception as e:
                print(f"[PIPELINE META] Error in policy engine update: {e}")
                
        if ENABLE_POLICY_DECAY:
            try:
                from app.meta.policy_decay_engine import decay_meta_memory
                decay_meta_memory()
            except Exception as e:
                print(f"[PIPELINE META] Error running meta decay: {e}")
                
        if ENABLE_POLICY_PRUNER:
            try:
                from app.meta.policy_pruner import prune_meta_memory
                from app.config import POLICY_PRUNE_INTERVAL
                tq = get_total_queries()
                if tq > 0 and tq % POLICY_PRUNE_INTERVAL == 0:
                    prune_meta_memory()
            except Exception as e:
                print(f"[PIPELINE META] Error running meta pruner: {e}")

        # Update debug metrics
        _latest_agent_debug = {
            "goal": goal_node,
            "plan": plan_node,
            "tasks": tasks,
            "executed_tools": executed_tools,
            "observations": observations,
            "reflections": reflections,
            "trace": trace_dict
        }
        
        # Log latency
        t_agent_end = time.time()
        record_latency((t_agent_end - t_agent_start) * 1000.0)
        increment_query()
        
        # Post-execution reinforcement and decay
        if ENABLE_HUMAN_PREFERENCES:
            try:
                from app.personality.personality_store import get_preferences
                from app.personality.preference_drift_engine import detect_preference_drift
                prefs = get_preferences()
                old_pref = prefs[0].tone_preference if prefs else "default"
                detect_preference_drift(old_pref, resolved_query)
                
                from app.personality.personality_reinforcement_engine import reinforce_personality
                reinforce_personality(selected_personality, success=success_turn)
                
                from app.personality.personality_pruner import increment_query_counter
                increment_query_counter()
                
                from app.personality.personality_decay_engine import decay_personality_memory
                decay_personality_memory()
            except Exception as e:
                print(f"[PIPELINE PERSONALITY] Post-execution error: {e}")

        return response
        
    else:
        # ---------------- ORIGINAL MULTI-TURN PIPELINE ----------------
        t_mem_start = time.time()
        increment_query()
        resolved_query = resolve_followup(query, session_id) if ENABLE_MEMORY else query
        
        # Retrieve personality context for fallback
        personality_context = None
        selected_personality = "concise engineer"
        if ENABLE_HUMAN_PREFERENCES:
            try:
                from app.personality.personality_retriever import get_relevant_preferences
                from app.personality.personality_optimizer import select_adaptive_personality
                from app.personality.adaptive_personality_engine import get_or_create_personality
                
                relevant_prefs = [p[0] for p in get_relevant_preferences(resolved_query)]
                selected_personality = select_adaptive_personality(resolved_query)
                pers_node = get_or_create_personality(selected_personality)
                
                personality_context = {
                    "preferences": relevant_prefs,
                    "selected_personality": selected_personality,
                    "speaking_patterns": pers_node.speaking_patterns if pers_node else [],
                    "explanation_preferences": pers_node.explanation_preferences if pers_node else []
                }
            except Exception as e:
                print(f"[PIPELINE PERSONALITY] Error retrieving personalization data in fallback: {e}")

        if resolved_query != query:
            increment_hit()
            
        if ENABLE_MEMORY:
            update_preferences_from_query(session_id, resolved_query)
            memory_nodes = retrieve_memories(session_id)
            ranked_memories = rank_memory_nodes(memory_nodes, resolved_query)
            if len(ranked_memories) > 0:
                increment_cache_hit()
        else:
            ranked_memories = []
            
        raw_evidence = retrieve_evidence(resolved_query)
        ranked_evidence = rank_evidence(raw_evidence, resolved_query)
        filtered_evidence = filter_irrelevant_nodes(resolved_query, ranked_evidence)
        entity_consensus = aggregate_entity_consensus(filtered_evidence)
        consensus_score, supporting_modalities = evaluate_consensus(filtered_evidence)
        compressed_evidence = compress_evidence(filtered_evidence)
        
        kg_context = None
        if ENABLE_KNOWLEDGE_GRAPH:
            kg_context = retrieve_knowledge(resolved_query, session_id)
            
        learning_context = None
        if ENABLE_SELF_LEARNING:
            learning_context = retrieve_learning_context(resolved_query)
            
        # Retrieve Episodic Memory context
        episodic_context = None
        if ENABLE_EPISODIC_MEMORY:
            from app.episodic.episodic_retriever import retrieve_episodic_context
            episodic_context = retrieve_episodic_context(resolved_query)
            
        # Retrieve Simulation context
        simulation_context = None
        if ENABLE_SIMULATION_ENGINE:
            from app.simulation.simulation_retriever import retrieve_simulation_context
            simulation_context = retrieve_simulation_context(resolved_query)

        context = build_context(
            compressed_evidence, 
            resolved_query, 
            session_id=session_id if ENABLE_MEMORY else None, 
            memory_nodes=ranked_memories,
            kg_context=kg_context,
            learning_context=learning_context,
            episodic_context=episodic_context,
            simulation_context=simulation_context,
            personality_context=personality_context
        )
        
        raw_answer = ollama_client.generate_response(query=resolved_query, context=context)
        
        if ENABLE_MEMORY and (is_meta_query(query) or is_meta_query(resolved_query)):
            final_answer = raw_answer
            grounding_report = [{"claim": "Bypassed for meta-query", "status": "Supported"}]
        else:
            final_answer, grounding_report = validate_grounding(raw_answer, filtered_evidence)
            
        citations = generate_citations(filtered_evidence)
        why_this_answer = generate_why_this_answer(filtered_evidence)
        
        top_score = filtered_evidence[0].retrieval_score if filtered_evidence else 0.0
        final_confidence_score = min(top_score + consensus_score, 1.0)
        confidence_label = "High" if final_confidence_score >= 0.80 else ("Medium" if final_confidence_score >= 0.50 else "Low")
        
        entities_debug = {}
        for c_node in entity_consensus:
            srcs = set()
            for node in filtered_evidence:
                if c_node.entity in get_node_entities(node.content).union(get_node_entities(node.source)):
                    srcs.add(node.source)
            ent_consensus_score = min(top_score + c_node.consensus_score, 1.0)
            entities_debug[c_node.entity] = {
                "modalities": c_node.modalities,
                "sources": sorted(list(srcs)),
                "consensus_score": round(ent_consensus_score, 4)
            }
        _latest_entities_debug = entities_debug
        
        if ENABLE_MEMORY:
            importance_score = calculate_importance(query, final_answer, citations, final_confidence_score)
            if importance_score >= 0.3:
                turn = ConversationTurn(
                    turn_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_query=query,
                    assistant_answer=final_answer,
                    timestamp=datetime.utcnow().isoformat(),
                    retrieved_sources=[c["source"] for c in citations],
                    entities=list(get_node_entities(resolved_query).union(get_node_entities(final_answer))),
                    intent_profile="",
                    confidence=confidence_label
                )
                add_turn(session_id, turn)
                update_entity_memories(session_id, resolved_query, final_answer, [c["source"] for c in citations], supporting_modalities, final_confidence_score)
                track_active_entities(session_id, resolved_query, final_answer)
                compress_older_turns(session_id)
                summarize_session_if_needed(session_id)
            record_latency((time.time() - t_mem_start) * 1000.0)
            
        # Evolve knowledge graph with current turn data
        update_knowledge_graph(
            query=query,
            final_answer=final_answer,
            session_id=session_id,
            filtered_evidence=filtered_evidence
        )
        
        # Update self-learning layer
        if ENABLE_SELF_LEARNING:
            try:
                has_refutations = False
                if grounding_report:
                    has_refutations = any(str(item.get("status", "")).lower() == "refuted" for item in grounding_report)
                
                success = ("not available" not in final_answer.lower()) and not has_refutations
                
                feedback_type = "SUCCESS"
                if not success:
                    feedback_type = "CORRECTION" if has_refutations else "FAILURE"
                elif confidence_label.lower() == "low":
                    feedback_type = "LOW_CONFIDENCE"
                    
                compile_and_store_feedback(
                    query=query,
                    answer=final_answer,
                    feedback_type=feedback_type,
                    confidence_label=confidence_label,
                    grounding_report=grounding_report
                )
                
                evidence_ids = []
                source_modalities = []
                for node in filtered_evidence:
                    if isinstance(node, dict):
                        ev_id = node.get("evidence_id") or node.get("id")
                        mod = node.get("modality") or "text"
                    else:
                        ev_id = getattr(node, "evidence_id", None) or getattr(node, "id", None)
                        mod = getattr(node, "modality", "text")
                    if ev_id:
                        evidence_ids.append(str(ev_id))
                    if mod:
                        source_modalities.append(str(mod))
                        
                compile_and_store_pattern(
                    query=resolved_query,
                    entity_set=get_node_entities(resolved_query),
                    intent_type="general",
                    success=success,
                    evidence_ids=evidence_ids,
                    source_modalities=source_modalities
                )
                
                evaluate_active_learning(
                    query=resolved_query,
                    answer=final_answer,
                    confidence_label=confidence_label,
                    grounding_report=grounding_report
                )
                
                cluster_query(query=resolved_query, success=success)
                
                total_queries = get_total_queries()
                if total_queries > 0 and total_queries % PATTERN_PRUNE_INTERVAL == 0:
                    decay_learning_memory()
                    prune_learning_memory()
            except Exception as e:
                print(f"[LEARNING PIPELINE] Error updating self-learning: {e}")
                
        # Evolve episodic memory
        if ENABLE_EPISODIC_MEMORY:
            try:
                from app.episodic.episode_builder import build_and_store_episode
                from app.episodic.temporal_memory_engine import update_temporal_chains
                from app.episodic.episode_cluster_engine import cluster_episode
                from app.episodic.experience_replay_engine import record_replay
                from app.episodic.memory_decay_engine import decay_episodic_memory
                from app.episodic.memory_pruner import prune_episodic_memory
                from app.config import ENABLE_MEMORY_DECAY, ENABLE_MEMORY_PRUNER, EPISODE_PRUNE_INTERVAL
                
                success = "not available" not in final_answer.lower()
                
                ep_node, exp_node = build_and_store_episode(
                    query=query,
                    answer=final_answer,
                    confidence_label_or_score=final_confidence_score,
                    grounding_report=grounding_report,
                    user_signal=1.0,
                    experience_type="standard_rag",
                    supporting_evidence_ids=[getattr(n, "evidence_id", None) or n.get("evidence_id") for n in filtered_evidence if (getattr(n, "evidence_id", None) or n.get("evidence_id"))],
                    success_status=success,
                    execution_latency=(time.time() - t_mem_start) * 1000.0
                )
                
                if ep_node:
                    update_temporal_chains(ep_node)
                    cluster_episode(ep_node)
                    
                    # Record reinforcement replays
                    for old_ep in episodic_context.get("episodes", []):
                        record_replay(old_ep.episode_id, ep_node.episode_id, 0.9, 1.0)
                        
                if ENABLE_MEMORY_DECAY:
                    decay_episodic_memory()
                    
                if ENABLE_MEMORY_PRUNER and get_total_queries() > 0 and get_total_queries() % EPISODE_PRUNE_INTERVAL == 0:
                    prune_episodic_memory()
            except Exception as e:
                print(f"[PIPELINE FALLBACK EPISODIC] Error during episodic memory storage: {e}")
                
        # Simulation explainability integration
        if ENABLE_SIMULATION_ENGINE:
            try:
                from app.simulation.simulation_explanation_engine import compile_simulation_explanation
                from app.simulation.simulation_store import get_scenarios, get_failure_forecasts
                sim_expl = compile_simulation_explanation(get_scenarios(), get_failure_forecasts())
            except Exception as e:
                print(f"[PIPELINE SIMULATION] Error generating explanation: {e}")
                sim_expl = ""

        # Simulation database updates, decay, and pruner
        if ENABLE_SIMULATION_ENGINE:
            try:
                from app.simulation.simulation_engine import record_simulation_run
                from app.simulation.simulation_decay_engine import decay_simulation_memory
                from app.simulation.simulation_pruner import prune_simulation_memory
                from app.simulation.world_state_compressor import compress_current_world_state
                from app.config import SIMULATION_PRUNE_INTERVAL
                
                success_status = "not available" not in final_answer.lower()
                score = 1.0 if success_status else 0.0
                
                # Compress world state on fallback too
                current_state = compress_current_world_state()
                initial_state_id = current_state.world_state_id
                final_state_id = f"ws_final_{uuid.uuid4().hex[:8]}"
                
                record_simulation_run(
                    initial_state_id=initial_state_id,
                    final_state_id=final_state_id,
                    scenario_chain=[],
                    score=score,
                    planner_trace_ids=[],
                    agent_ids=[],
                    tool_ids=[]
                )
                
                decay_simulation_memory()
                
                tq = get_total_queries()
                if tq > 0 and tq % SIMULATION_PRUNE_INTERVAL == 0:
                    prune_simulation_memory()
            except Exception as e:
                print(f"[PIPELINE SIMULATION] Error in post-execution updates: {e}")
                
        # Inject explanation to response if episodic/simulation explanations are enabled
        payload = {
            "answer": final_answer,
            "resolved_query": resolved_query,
            "session_id": session_id,
            "confidence": confidence_label,
            "confidence_score": round(final_confidence_score, 4),
            "sources": citations,
            "evidence": [node.dict() for node in filtered_evidence],
            "why_this_answer": why_this_answer,
            "supporting_modalities": supporting_modalities,
            "debug_details": {
                "query": query,
                "resolved_query": resolved_query,
                "raw_answer": raw_answer,
                "grounding_report": grounding_report,
                "consensus_score": consensus_score,
                "compressed_context_size": len(context)
            }
        }
        explanation = ""
        if ENABLE_HUMAN_PREFERENCES:
            try:
                from app.personality.personality_explanation_engine import compile_personality_explanation
                pers_expl = compile_personality_explanation(
                    preference_applied=True,
                    personality_type=selected_personality
                )
                if pers_expl:
                    explanation = pers_expl + "\n"
            except Exception as e:
                print(f"[PIPELINE PERSONALITY] Error compiling fallback explanation: {e}")

        if ENABLE_EPISODIC_MEMORY and episodic_context:
            from app.episodic.episodic_explanation_engine import compile_episodic_explanation
            epis_expl = compile_episodic_explanation(episodic_context.get("replays", []))
            if epis_expl:
                explanation += epis_expl + "\n"
        if ENABLE_SIMULATION_ENGINE and 'sim_expl' in locals() and sim_expl:
            explanation = sim_expl + "\n" + explanation
            
        if explanation:
            payload["explanation"] = explanation

        # Post-execution reinforcement and decay for fallback
        if ENABLE_HUMAN_PREFERENCES:
            try:
                from app.personality.personality_store import get_preferences
                from app.personality.preference_drift_engine import detect_preference_drift
                prefs = get_preferences()
                old_pref = prefs[0].tone_preference if prefs else "default"
                detect_preference_drift(old_pref, resolved_query)
                
                from app.personality.personality_reinforcement_engine import reinforce_personality
                reinforce_personality(selected_personality, success=success)
                
                from app.personality.personality_pruner import increment_query_counter
                increment_query_counter()
                
                from app.personality.personality_decay_engine import decay_personality_memory
                decay_personality_memory()
            except Exception as e:
                print(f"[PIPELINE PERSONALITY] Post-execution error in fallback: {e}")

        return payload
