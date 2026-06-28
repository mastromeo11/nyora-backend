import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import UPLOAD_DIR
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text
from app.llm.ollama_client import ollama_client
from app.retrieval.image_retriever import retrieve_images
from app.retrieval.fusion_retriever import retrieve_multimodal

app = FastAPI(title="Offline Multimodal RAG Backend - Milestone 1")

# Configure CORS Middleware for Lovable frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    limit: int = 5

class ImageSearchRequest(BaseModel):
    query: str
    limit: int = 5

class MultimodalSearchRequest(BaseModel):
    query: str
    text_limit: int = 3
    image_limit: int = 3

class VisualQuestionRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    """
    Checks connection to local persistent ChromaDB.
    """
    db_status = "connected"
    try:
        db.client.heartbeat()
    except Exception:
        db_status = "disconnected"
        
    llm_status = "connected"
    try:
        import requests
        from app.config import OLLAMA_URL
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if resp.status_code != 200:
            llm_status = "disconnected"
    except Exception:
        llm_status = "disconnected"
    
    return {
        "status": "ok" if (db_status == "connected" and llm_status == "connected") else "error",
        "vector_db": db_status,
        "llm": llm_status
    }

@app.post("/ingest")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles PDF document uploads and triggers the parser ingestion pipeline.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    res = ingest_file(file_path, file.filename)
    
    if res.get("status") == "error":
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=res.get("message"))
        
    return res

@app.post("/query")
def query_system(req: QueryRequest):
    """
    Accepts text queries and retrieves relevant context chunks.
    """
    try:
        # Retrieve context chunks
        chunks = retrieve_text(req.query, n_results=req.limit)
        
        # Combine chunk texts for prompt context with source headers
        context_items = []
        for chunk in chunks:
            source_info = f"Source: {chunk['source']}"
            if chunk.get('page') is not None:
                source_info += f" (Page {chunk['page']})"
            context_items.append(f"[{source_info}]\n{chunk['text']}")
        context = "\n\n".join(context_items)
        
        # Generate answer from local LLM
        answer = ollama_client.generate_response(query=req.query, context=context)

        
        return {
            "query": req.query,
            "answer": answer,
            "retrieved_chunks": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-images")
def search_images_endpoint(req: ImageSearchRequest):
    """
    Exposes CLIP-based visual semantic search over images.
    """
    try:
        results = retrieve_images(req.query, limit=req.limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-multimodal")
def search_multimodal_endpoint(req: MultimodalSearchRequest):
    """
    Exposes dual-pathway text and visual retrieval.
    """
    try:
        results = retrieve_multimodal(
            query=req.query,
            text_limit=req.text_limit,
            image_limit=req.image_limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/retrieval")
def debug_retrieval_endpoint(query: str):
    """
    Diagnostic endpoint that returns raw scores, confidence mappings,
    visual categories, blank status, and final fusion scores for evaluation.
    """
    try:
        results = retrieve_multimodal(query, text_limit=5, image_limit=5)
        return {
            "query": query,
            "detected_intent": results.get("query_intent"),
            "fused_results": results.get("fused_results"),
            "raw_text_results": results.get("text_results"),
            "raw_image_results": results.get("image_results")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visual-qa")
def visual_qa_endpoint(req: VisualQuestionRequest):
    """
    Executes Visual Question Answering (VQA) using LLaVA on the retrieved candidate images.
    """
    try:
        from app.retrieval.visual_qa_pipeline import answer_visual_question
        res = answer_visual_question(req.question)
        ret = {
            "answer": res["answer"],
            "source_image": res["source_image"],
            "file_path": res["file_path"],
            "visual_category": res["visual_category"],
            "caption": res["caption"],
            "clip_score": res["clip_score"],
            "confidence": res["confidence"],
            "model_used": res["model_used"]
        }
        if "citation_reason" in res:
            ret["citation_reason"] = res["citation_reason"]
        return ret
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/vqa")
def debug_vqa_endpoint(question: str):
    """
    Diagnostic visual QA endpoint detailing candidate visual matches and answers.
    """
    try:
        from app.retrieval.visual_qa_pipeline import answer_visual_question
        res = answer_visual_question(question)
        return {
            "query": question,
            "selected_image": res["source_image"],
            "clip_score": res["clip_score"],
            "confidence": res["confidence"],
            "visual_category": res["visual_category"],
            "caption": res["caption"],
            "candidate_list": res["all_candidates"],
            "retrieval_reason": res.get("citation_reason", "No explanations compiled."),
            "answer": res["answer"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-route")
def query_route_endpoint(req: QueryRequest):
    """
    Unified router routing queries to standard text RAG, visual QA, or multimodal search pathways.
    In Milestone 8, all paths are converged into Unified Evidence RAG.
    """
    try:
        from app.retrieval.query_router import route_query
        res = route_query(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-unified")
def query_unified_endpoint(req: QueryRequest):
    """
    Direct endpoint for Production-Grade Unified Evidence RAG.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        res = answer_query(req.query)
        # Exclude raw Pydantic EvidenceNode objects from standard JSON output
        # to ensure clean serializability (or serialize them into dicts)
        serializable_evidence = [node.dict() if hasattr(node, "dict") else node for node in res.get("evidence", [])]
        res["evidence"] = serializable_evidence
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/evidence")
def debug_evidence_endpoint(query: str):
    """
    Diagnostic dashboard endpoint returning rankings, graph data, and citations.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        from app.retrieval.debug_evidence import format_ranking_details
        from app.retrieval.evidence_graph import build_evidence_graph
        from app.retrieval.context_builder import build_context
        
        res = answer_query(query)
        evidence_list = res["evidence"]
        
        graph_data = build_evidence_graph(evidence_list)
        context_str = build_context(evidence_list)
        
        return {
            "query": query,
            "ranked_evidence": format_ranking_details(evidence_list),
            "graph_nodes": graph_data["nodes"],
            "edges": graph_data["edges"],
            "context": context_str,
            "citations": res["sources"],
            "reasons": res["why_this_answer"],
            "confidence": res["confidence"],
            "confidence_score": res["confidence_score"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/graph")
def debug_graph_endpoint(query: str):
    """
    Diagnostic endpoint returning graph nodes and links.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        from app.retrieval.evidence_graph import build_evidence_graph
        res = answer_query(query)
        graph_data = build_evidence_graph(res["evidence"])
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/context")
def debug_context_endpoint(query: str):
    """
    Diagnostic endpoint returning compressed context strings.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        from app.retrieval.evidence_compressor import compress_evidence
        from app.retrieval.context_builder import build_context
        res = answer_query(query)
        compressed = compress_evidence(res["evidence"])
        context_str = build_context(compressed)
        return {"query": query, "context": context_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/grounding")
def debug_grounding_endpoint(query: str):
    """
    Diagnostic endpoint returning factual claims verification report.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        res = answer_query(query)
        return {
            "query": query,
            "answer": res["answer"],
            "grounding_report": res["debug_details"]["grounding_report"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/entities")
def debug_entities_endpoint(query: str):
    """
    Diagnostic endpoint returning entity-centric consensus details.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query, get_latest_entities_debug
        answer_query(query)
        return get_latest_entities_debug()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/relevance")
def debug_relevance_endpoint(query: str):
    """
    Diagnostic endpoint returning details on pruned/removed irrelevant nodes.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        from app.retrieval.relevance_filter import get_latest_relevance_diagnostics
        answer_query(query)
        return get_latest_relevance_diagnostics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Milestone 9: Conversational Memory Endpoints ---

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    """
    Unified memory-aware multi-turn conversational chat endpoint.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        res = answer_query(req.query, session_id=req.session_id)
        # Convert raw EvidenceNode items in the list to serialized dicts
        res["evidence"] = [node.dict() if hasattr(node, "dict") else node for node in res.get("evidence", [])]
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/session")
def memory_session_endpoint(session_id: str):
    """
    Returns all short-term conversation turns in the active session.
    """
    try:
        from app.retrieval.session_memory import get_session
        turns = get_session(session_id)
        return [t.dict() for t in turns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/entities")
def memory_entities_endpoint(session_id: str):
    """
    Returns all entity memories gathered inside the session.
    """
    try:
        from app.retrieval.memory_cache import get_session_cache
        data = get_session_cache(session_id)
        return data.get("entity_memories", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/summary")
def memory_summary_endpoint(session_id: str):
    """
    Returns all conversational summaries for the session.
    """
    try:
        from app.retrieval.memory_cache import get_session_cache
        data = get_session_cache(session_id)
        return data.get("summaries", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/graph")
def memory_graph_endpoint(query: str, session_id: str):
    """
    Returns the extended memory graph showing turns, entity nodes, summary nodes,
    preferences, and evidence nodes linked semantically.
    """
    try:
        from app.retrieval.unified_pipeline import answer_query
        from app.retrieval.memory_graph import build_memory_graph
        res = answer_query(query, session_id=session_id)
        graph_data = build_memory_graph(res["evidence"], session_id=session_id)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/cache")
def memory_cache_endpoint(session_id: str):
    """
    Returns the raw session cache dictionary containing active memory records.
    """
    try:
        from app.retrieval.memory_cache import get_session_cache
        return get_session_cache(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/active-entity")
def memory_active_entity_endpoint(session_id: str):
    """
    Returns the current and previous active entity focus values.
    """
    try:
        from app.retrieval.memory_cache import get_session_cache
        data = get_session_cache(session_id)
        return {
            "current_entity_focus": data.get("current_entity_focus"),
            "previous_entity_focus": data.get("previous_entity_focus")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/memory")
def debug_memory_endpoint(session_id: str):
    """
    Returns all memory nodes in a flattened format (turns, summaries, entities, preferences).
    """
    try:
        from app.retrieval.memory_retriever import retrieve_memories
        nodes = retrieve_memories(session_id)
        return [node.dict() if hasattr(node, "dict") else node for node in nodes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/followup")
def debug_followup_endpoint():
    """
    Returns the detailed pronoun resolution diagnosis from the latest turn.
    """
    try:
        from app.retrieval.followup_resolver import get_latest_followup_debug
        return get_latest_followup_debug()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/session")
def debug_session_endpoint(session_id: str):
    """
    Returns the last 10 turns stored in active session.
    """
    try:
        from app.retrieval.session_memory import get_recent_turns
        turns = get_recent_turns(session_id, 10)
        return [t.dict() for t in turns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/entity-focus")
def debug_entity_focus_endpoint(session_id: str):
    """
    Returns decayed entity focus scores for active topic scoring.
    """
    try:
        from app.retrieval.entity_decay_engine import compute_entity_scores
        return compute_entity_scores(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/clear")
def memory_clear_endpoint(session_id: str):
    """
    Clears the conversational turn history and active caches for the session.
    """
    try:
        from app.retrieval.session_memory import clear_session
        from app.retrieval.memory_cache import save_session_cache
        clear_session(session_id)
        save_session_cache(session_id, {
            "active_entities": [],
            "current_entity_focus": None,
            "previous_entity_focus": None,
            "conversation_topic": None,
            "entity_memories": {},
            "preference_memory": {},
            "summaries": []
        })
        return {"status": "success", "message": f"Cleared memory for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/memory-explanation")
def debug_memory_explanation_endpoint():
    """
    Returns structured memory explanation diagnostics from the latest turn.
    """
    try:
        from app.retrieval.memory_explanation_engine import get_latest_memory_explanation
        return get_latest_memory_explanation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/metrics")
def debug_metrics_endpoint():
    """
    Exposes the tracked memory quality statistics.
    """
    try:
        from app.retrieval.memory_metrics import get_metrics
        return get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AgentChatRequest(BaseModel):
    query: str
    session_id: str

@app.post("/agent/chat")
def agent_chat_endpoint(req: AgentChatRequest):
    try:
        from app.retrieval.unified_pipeline import answer_query
        res = answer_query(req.query, session_id=req.session_id)
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/goals")
def agent_goals_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        goal = debug.get("goal")
        if isinstance(goal, dict):
            return [goal]
        return [goal.dict()] if goal else []
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/plans")
def agent_plans_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        plan = debug.get("plan")
        if isinstance(plan, dict):
            return [plan]
        return [plan.dict()] if plan else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/tasks")
def agent_tasks_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        tasks = debug.get("tasks", [])
        return [t if isinstance(t, dict) else t.dict() for t in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/observations")
def agent_observations_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        obs = debug.get("observations", [])
        return [o if isinstance(o, dict) else o.dict() for o in obs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/reflections")
def agent_reflections_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        refls = debug.get("reflections", [])
        return [r if isinstance(r, dict) else r.dict() for r in refls]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/traces")
def agent_traces_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        trace = debug.get("trace")
        return [trace] if trace else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/graph")
def agent_graph_endpoint(session_id: str):
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        from app.retrieval.agent_graph import build_agent_graph
        debug = get_latest_agent_debug()
        goal = debug.get("goal")
        plan = debug.get("plan")
        tasks = debug.get("tasks", [])
        executed_tools = debug.get("executed_tools", [])
        observations = debug.get("observations", [])
        reflections = debug.get("reflections", [])
        trace = debug.get("trace")
        
        evidence_list = []
        
        graph_data = build_agent_graph(
            evidence_list=evidence_list,
            session_id=session_id,
            goal=goal,
            plan=plan,
            tasks=tasks,
            executed_tools=executed_tools,
            observations=observations,
            reflections=reflections,
            trace=trace
        )
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/agent")
def debug_agent_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        goal = debug.get("goal")
        plan = debug.get("plan")
        return {
            "goal": goal if isinstance(goal, dict) else (goal.dict() if goal else None),
            "plan": plan if isinstance(plan, dict) else (plan.dict() if plan else None),
            "tasks_count": len(debug.get("tasks", [])),
            "executed_tools_count": len(debug.get("executed_tools", [])),
            "observations_count": len(debug.get("observations", [])),
            "reflections_count": len(debug.get("reflections", []))
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/react")
def debug_react_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        obs = debug.get("observations", [])
        return {"observations": [o if isinstance(o, dict) else o.dict() for o in obs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/tools")
def debug_tools_endpoint():
    try:
        from app.retrieval.unified_pipeline import get_latest_agent_debug
        debug = get_latest_agent_debug()
        tools = debug.get("executed_tools", [])
        return [t if isinstance(t, dict) else t.dict() for t in tools]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/reset")
def agent_reset_endpoint():
    try:
        from app.retrieval.unified_pipeline import reset_latest_agent_debug
        reset_latest_agent_debug()
        return {"status": "success", "message": "Cleared agent reasoning trace states."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Milestone 11: Knowledge Graph Endpoints ---

@app.get("/debug/graph-explanation")
def debug_graph_explanation_endpoint():
    """
    Returns structured knowledge graph explanation diagnostics from the latest turn.
    """
    try:
        from app.retrieval.graph_explanation_engine import get_latest_graph_explanation
        return get_latest_graph_explanation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/knowledge-graph")
def debug_knowledge_graph_endpoint():
    """
    Returns the persistent knowledge graph store representation.
    """
    try:
        from app.retrieval.graph_store import load_graph
        return load_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/clear")
def knowledge_clear_endpoint():
    """
    Resets/clears the persistent knowledge graph store.
    """
    try:
        from app.retrieval.graph_store import clear_graph_store
        clear_graph_store()
        return {"status": "success", "message": "Cleared the semantic knowledge graph store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/graph-cache")
def debug_graph_cache_endpoint():
    """
    Returns knowledge graph LRU caching hit rates and occupancy.
    """
    try:
        from app.retrieval.graph_cache import get_cache_metrics
        return get_cache_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Milestone 12: Self-Learning Endpoints ---

@app.get("/learning/patterns")
def get_learning_patterns():
    try:
        from app.learning.learning_store import get_patterns
        return [pat.dict() for pat in get_patterns()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/corrections")
def get_learning_corrections():
    try:
        from app.learning.learning_store import get_corrections
        return [corr.dict() for corr in get_corrections()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/clusters")
def get_learning_clusters():
    try:
        from app.learning.learning_store import get_clusters
        return [clust.dict() for clust in get_clusters()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/failures")
def get_learning_failures():
    try:
        from app.learning.learning_store import get_failure_patterns
        return [fail.dict() for fail in get_failure_patterns()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/cache")
def get_learning_cache():
    try:
        from app.learning.learning_cache import get_learning_cache_metrics
        return get_learning_cache_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LearningQueryRequest(BaseModel):
    query: str

@app.post("/learning/query")
def learning_query_endpoint(req: LearningQueryRequest):
    try:
        from app.learning.learning_retriever import retrieve_learning_context
        return retrieve_learning_context(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/clear")
def learning_clear_endpoint():
    try:
        from app.learning.learning_store import clear_learning_store
        clear_learning_store()
        return {"status": "success", "message": "Cleared the self-learning memory store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Debug routes:
@app.get("/debug/patterns")
def debug_patterns_endpoint():
    return get_learning_patterns()

@app.get("/debug/corrections")
def debug_corrections_endpoint():
    return get_learning_corrections()

@app.get("/debug/clusters")
def debug_clusters_endpoint():
    return get_learning_clusters()

@app.get("/debug/failures")
def debug_failures_endpoint():
    return get_learning_failures()

@app.get("/debug/learning-graph")
def debug_learning_graph_endpoint():
    try:
        from app.retrieval.graph_store import load_graph
        from app.learning.learning_graph import extend_learning_graph
        from app.learning.learning_store import (
            get_patterns, get_corrections, get_feedback, get_clusters, get_failure_patterns
        )
        base_graph = load_graph()
        extended = extend_learning_graph(
            base_graph=base_graph,
            patterns=get_patterns(),
            corrections=get_corrections(),
            feedbacks=get_feedback(),
            clusters=get_clusters(),
            failures=get_failure_patterns()
        )
        return extended
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Milestone 13: Multi-Agent Swarm Endpoints ---

@app.get("/swarm/agents")
def get_swarm_agents_endpoint():
    try:
        from app.swarm.agent_store import load_swarm_store
        store = load_swarm_store()
        return store.get("agents", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarm/messages")
def get_swarm_messages_endpoint():
    try:
        from app.swarm.agent_store import load_swarm_store
        store = load_swarm_store()
        return store.get("messages", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarm/shared-memory")
def get_swarm_shared_memory_endpoint():
    try:
        from app.swarm.shared_memory import get_shared_memory_state
        return get_shared_memory_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarm/negotiations")
def get_swarm_negotiations_endpoint():
    try:
        from app.swarm.agent_store import load_swarm_store
        store = load_swarm_store()
        return {
            "consensus_nodes": store.get("consensus_nodes", []),
            "shared_memory_negotiations": [
                val for key, val in store.get("shared_memory", {}).items() if "negotiation" in key or "consensus" in key
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarm/graph")
def get_swarm_graph_endpoint():
    try:
        from app.retrieval.graph_store import load_graph
        from app.swarm.swarm_graph import extend_swarm_graph
        from app.swarm.agent_store import load_swarm_store
        
        base_graph = load_graph()
        store = load_swarm_store()
        
        agents = list(store.get("agents", {}).values())
        messages = store.get("messages", [])
        delegations = store.get("delegations", [])
        collaborations = store.get("collaborations", [])
        consensus_nodes = store.get("consensus_nodes", [])
        
        shared_memory_list = list(store.get("shared_memory", {}).values())
        
        extended = extend_swarm_graph(
            base_graph=base_graph,
            agents=agents,
            messages=messages,
            delegations=delegations,
            collaborations=collaborations,
            consensus_nodes=consensus_nodes,
            shared_memories=shared_memory_list
        )
        return extended
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swarm/clear")
def post_swarm_clear_endpoint():
    try:
        from app.swarm.agent_store import clear_swarm_store
        from app.swarm.shared_memory import clear_shared_memory
        from app.swarm.message_broker import clear_broker
        from app.swarm.agent_monitor import clear_agent_monitor
        from app.swarm.communication_graph import clear_communication_graph
        from app.swarm.agent_cache import clear_all_agent_caches
        
        clear_swarm_store()
        clear_shared_memory()
        clear_broker()
        clear_agent_monitor()
        clear_communication_graph()
        clear_all_agent_caches()
        
        return {"status": "success", "message": "Cleared all multi-agent swarm state and history."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Milestone 14: Episodic Memory Endpoints ---

@app.get("/episodes")
def get_episodes_endpoint():
    try:
        from app.episodic.episodic_store import get_episodes
        return [ep.model_dump() for ep in get_episodes()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/episodes/replays")
def get_episodes_replays_endpoint():
    try:
        from app.episodic.episodic_store import get_replays
        return [rep.model_dump() for rep in get_replays()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/episodes/chains")
def get_episodes_chains_endpoint():
    try:
        from app.episodic.episodic_store import get_chains
        return [ch.model_dump() for ch in get_chains()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/episodes/clusters")
def get_episodes_clusters_endpoint():
    try:
        from app.episodic.episodic_store import get_clusters
        return [cl.model_dump() for cl in get_clusters()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/episodes/cache")
def get_episodes_cache_endpoint():
    try:
        from app.episodic.episodic_cache import get_episodic_cache_metrics
        return get_episodic_cache_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/episodes/query")
def post_episodes_query_endpoint(req: QueryRequest):
    try:
        from app.episodic.episodic_retriever import retrieve_episodic_context
        res = retrieve_episodic_context(req.query, limit=req.limit)
        return {
            "episodes": [ep.model_dump() for ep in res["episodes"]],
            "replays": [rep.model_dump() for rep in res["replays"]],
            "chains": [ch.model_dump() for ch in res["chains"]],
            "clusters": [cl.model_dump() for cl in res["clusters"]],
            "summaries": [s.model_dump() for s in res["summaries"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/episodes/clear")
def post_episodes_clear_endpoint():
    try:
        from app.episodic.episodic_store import clear_episodic_store
        from app.episodic.episodic_cache import clear_all_episodic_caches
        clear_episodic_store()
        clear_all_episodic_caches()
        return {"status": "success", "message": "Cleared all episodic memory state."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/episodes")
def debug_episodes_endpoint():
    try:
        from app.episodic.episodic_store import get_episodes
        return [ep.model_dump() for ep in get_episodes()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/replays")
def debug_replays_endpoint():
    try:
        from app.episodic.episodic_store import get_replays
        return [rep.model_dump() for rep in get_replays()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/chains")
def debug_chains_endpoint():
    try:
        from app.episodic.episodic_store import get_chains
        return [ch.model_dump() for ch in get_chains()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/clusters")
def debug_clusters_endpoint():
    try:
        from app.episodic.episodic_store import get_clusters
        return [cl.model_dump() for cl in get_clusters()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/episodic-summary")
def debug_episodic_summary_endpoint(chain_id: str):
    try:
        from app.episodic.episodic_store import get_chain_summaries
        summaries = get_chain_summaries()
        for s in summaries:
            if s.chain_id == chain_id:
                return s.model_dump()
        raise HTTPException(status_code=404, detail="No summary found for chain_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Milestone 15: Simulation & World Model Endpoints ---

@app.get("/world-states")
def get_world_states_endpoint():
    try:
        from app.simulation.simulation_store import get_world_states
        return [ws.model_dump() for ws in get_world_states()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hypotheses")
def get_hypotheses_endpoint():
    try:
        from app.simulation.simulation_store import get_hypotheses
        return [h.model_dump() for h in get_hypotheses()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scenarios")
def get_scenarios_endpoint():
    try:
        from app.simulation.simulation_store import get_scenarios
        return [sc.model_dump() for sc in get_scenarios()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/counterfactuals")
def get_counterfactuals_endpoint():
    try:
        from app.simulation.simulation_store import get_counterfactuals
        return [cf.model_dump() for cf in get_counterfactuals()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulations")
def get_simulations_endpoint():
    try:
        from app.simulation.simulation_store import get_simulations
        return [sim.model_dump() for sim in get_simulations()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policies")
def get_policies_endpoint():
    try:
        from app.config import ENABLE_PLANNER_POLICIES
        if ENABLE_PLANNER_POLICIES:
            from app.meta.meta_store import get_policies as get_meta_policies
            return [p.model_dump() for p in get_meta_policies()]
        from app.simulation.simulation_store import get_policies
        return [p.model_dump() for p in get_policies()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/failure-forecasts")
def get_failure_forecasts_endpoint():
    try:
        from app.simulation.simulation_store import get_failure_forecasts
        return [f.model_dump() for f in get_failure_forecasts()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation/cache")
def get_simulation_cache_endpoint():
    try:
        from app.simulation.world_model_cache import get_cache_hit_rate
        return {"hit_rate": get_cache_hit_rate()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/query")
def post_simulation_query_endpoint(req: QueryRequest):
    try:
        from app.simulation.simulation_retriever import retrieve_simulation_context
        res = retrieve_simulation_context(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/clear")
def post_simulation_clear_endpoint():
    try:
        from app.simulation.simulation_store import clear_simulation_store
        from app.simulation.world_model_cache import clear_all_simulation_caches
        clear_simulation_store()
        clear_all_simulation_caches()
        return {"status": "success", "message": "Cleared all simulation/world model state."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/world-model")
def debug_world_model_endpoint():
    try:
        from app.simulation.simulation_store import load_world_model_store
        return load_world_model_store()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policy-failures")
def get_policy_failures_endpoint():
    try:
        from app.config import ENABLE_PLANNER_POLICIES
        if ENABLE_PLANNER_POLICIES:
            from app.meta.meta_store import get_policy_failures as get_meta_policy_failures
            return [pf.model_dump() for pf in get_meta_policy_failures()]
        from app.simulation.simulation_store import get_policy_failures
        return [pf.model_dump() for pf in get_policy_failures()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation-archives")
def get_simulation_archives_endpoint():
    try:
        from app.simulation.simulation_store import get_simulation_archives
        return [sa.model_dump() for sa in get_simulation_archives()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Milestone 16 REST endpoints ---

@app.get("/tools")
def get_tools_endpoint():
    try:
        from app.meta.meta_store import get_tools
        return [t.model_dump() for t in get_tools()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies")
def get_strategies_endpoint():
    try:
        from app.meta.meta_store import get_strategies
        return [s.model_dump() for s in get_strategies()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reflections")
def get_reflections_endpoint():
    try:
        from app.meta.meta_store import get_reflections
        return [r.model_dump() for r in get_reflections()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/replays")
def get_replays_endpoint():
    try:
        from app.meta.meta_store import get_replays
        return [rep.model_dump() for rep in get_replays()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tool-failures")
def get_tool_failures_endpoint():
    try:
        from app.meta.meta_store import get_tool_failures
        return [tf.model_dump() for tf in get_tool_failures()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/optimization-failures")
def get_optimization_failures_endpoint():
    try:
        from app.meta.meta_store import get_optimization_failures
        return [of.model_dump() for of in get_optimization_failures()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policy-archives")
def get_policy_archives_endpoint():
    try:
        from app.meta.meta_store import get_archives
        return [pa.model_dump() for pa in get_archives()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meta-archives")
def get_meta_archives_endpoint():
    try:
        from app.meta.meta_store import get_meta_archives
        return [ma.model_dump() for ma in get_meta_archives()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meta/cache")
def get_meta_cache_endpoint():
    try:
        from app.meta.policy_cache import tools_cache, policies_cache
        return {
            "tools_cache_size": len(tools_cache.cache),
            "policies_cache_size": len(policies_cache.cache)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meta/query")
def post_meta_query_endpoint(req: QueryRequest):
    try:
        from app.meta.meta_retriever import retrieve_meta_context
        res = retrieve_meta_context(req.query)
        return {
            "tools": [t.model_dump() for t in res["tools"]],
            "policies": [p.model_dump() for p in res["policies"]],
            "strategies": [s.model_dump() for s in res["strategies"]],
            "reflections": [r.model_dump() for r in res["reflections"]],
            "replays": [rep.model_dump() for rep in res["replays"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meta/clear")
def post_meta_clear_endpoint():
    try:
        from app.meta.meta_store import clear_meta_store
        clear_meta_store()
        return {"status": "success", "message": "Cleared all meta-cognition store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/meta")
def get_debug_meta_endpoint():
    try:
        from app.meta.meta_store import load_meta_store
        return load_meta_store()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personality/preferences")
def get_personality_preferences():
    try:
        from app.personality.personality_store import get_preferences
        return [p.model_dump() for p in get_preferences()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personality/failures")
def get_personality_failures_endpoint():
    try:
        from app.personality.personality_store import get_personality_failures
        return [f.model_dump() for f in get_personality_failures()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/personality/preference")
def post_personality_preference(pref: dict):
    try:
        from app.personality.personality_models import HumanPreferenceNode
        from app.personality.personality_store import append_preference
        node = HumanPreferenceNode(**pref)
        append_preference(node)
        return {"status": "success", "preference": node.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/personality/clear")
def post_personality_clear():
    try:
        from app.personality.personality_store import clear_personality_store
        clear_personality_store()
        return {"status": "success", "message": "Cleared personality store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/personality")
def get_debug_personality():
    try:
        from app.personality.personality_store import load_personality_store
        return load_personality_store()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.ui.ui_api import router as ui_router
app.include_router(ui_router)


