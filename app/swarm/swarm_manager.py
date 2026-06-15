import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
from app.config import (
    ENABLE_MULTI_AGENT_SWARM,
    MAX_SWARM_STEPS,
    SWARM_TIMEOUT_SECONDS,
    ENABLE_CRITIC_AGENT
)
from app.swarm.agents.planner_agent import PlannerAgent
from app.swarm.agents.retrieval_agent import RetrievalAgent
from app.swarm.agents.kg_agent import KGAgent
from app.swarm.agents.learning_agent import LearningAgent
from app.swarm.agents.vqa_agent import VQAAgent
from app.swarm.agents.grounding_agent import GroundingAgent
from app.swarm.agents.critic_agent import CriticAgent
from app.swarm.shared_memory import clear_shared_memory, get_shared_memory_state, write_shared_memory
from app.swarm.message_broker import clear_broker
from app.swarm.agent_monitor import record_agent_execution
from app.swarm.negotiation_consensus import resolve_agent_consensus

class SwarmManager:
    def __init__(self):
        self.planner = PlannerAgent()
        self.retrieval = RetrievalAgent()
        self.kg = KGAgent()
        self.learning = LearningAgent()
        self.vqa = VQAAgent()
        self.grounding = GroundingAgent()
        self.critic = CriticAgent()
        
    def execute_swarm_query(self, query: str) -> Dict[str, Any]:
        """
        Orchestrates swarm task delegation, execution, criticism, negotiation, and grounding validation.
        """
        t_start = time.time()
        clear_shared_memory()
        clear_broker()
        
        history = []
        steps = 0
        
        def execute_step(agent, task_data):
            nonlocal steps
            steps += 1
            if steps > MAX_SWARM_STEPS:
                raise TimeoutError(f"[SWARM COORDINATOR] Capped execution at MAX_SWARM_STEPS = {MAX_SWARM_STEPS}")
                
            elapsed = time.time() - t_start
            if elapsed > SWARM_TIMEOUT_SECONDS:
                raise TimeoutError(f"[SWARM COORDINATOR] Swarm execution timed out after {elapsed:.2f} seconds.")
                
            t_exec_start = time.time()
            res = agent.execute_task(task_data)
            exec_time = (time.time() - t_exec_start) * 1000.0
            
            history.append({
                "step": steps,
                "agent_id": agent.agent_id,
                "task": task_data,
                "result": res,
                "latency_ms": exec_time
            })
            return res

        # Step 1: Planning / Decomposition
        plan_res = execute_step(self.planner, {"query": query})
        
        # Step 2: Context Retrieval
        ret_res = execute_step(self.retrieval, {"query": query})
        kg_res = execute_step(self.kg, {"query": query})
        learn_res = execute_step(self.learning, {"query": query})
        
        # Step 3: VQA check
        vqa_res = execute_step(self.vqa, {"query": query})
        
        # Extract outputs for criticism
        ret_evidence = ret_res.get("evidence", [])
        ret_text = " ".join([e.get("content", "") for e in ret_evidence])
        kg_context = kg_res.get("kg_context", {})
        kg_text = kg_context.get("natural_explanation", "") if isinstance(kg_context, dict) else str(kg_context)
        
        # Step 4: Criticism
        critic_res = {}
        if ENABLE_CRITIC_AGENT:
            critic_res = execute_step(self.critic, {
                "retrieval_output": ret_text,
                "kg_output": kg_text
            })
            
        # Step 5: Negotiation & Consensus if contradiction detected
        contradiction = critic_res.get("contradiction_detected", False)
        agreed_fact = ""
        consensus_score = 1.0
        
        if contradiction:
            proposals = [
                {"agent_id": "retrieval", "proposal": "Retrieval context is correct", "weight": 1.0, "confidence": 0.8},
                {"agent_id": "kg", "proposal": "KG context is correct", "weight": 1.0, "confidence": 0.8}
            ]
            con_res = resolve_agent_consensus(
                topic=critic_res.get("reason", "contradiction"),
                proposals=proposals,
                critic_feedback=critic_res
            )
            agreed_fact = con_res.get("agreed_fact", "")
            consensus_score = con_res.get("consensus_score", 1.0)
            
            write_shared_memory("negotiation_result", con_res, "coordinator")
            
        from app.retrieval.context_builder import build_context
        from app.llm.ollama_client import ollama_client
        from app.retrieval.evidence_models import EvidenceNode
        
        evidence_nodes = [EvidenceNode(**e) for e in ret_evidence]
        
        context = build_context(
            ranked_evidence=evidence_nodes,
            query=query,
            kg_context=kg_context,
            learning_context=learn_res.get("learning_context")
        )
        
        if agreed_fact:
            context = f"=== CONFLICT RESOLUTION CONSENSUS ===\nConsensus Fact: {agreed_fact}\nConfidence: {consensus_score:.2f}\n\n" + context
            
        raw_answer = ollama_client.generate_response(query=query, context=context)
        
        # Step 6: Grounding Validation
        ground_res = execute_step(self.grounding, {
            "answer": raw_answer,
            "evidence": ret_evidence
        })
        
        final_answer = ground_res.get("final_answer", raw_answer)
        
        from app.retrieval.citation_engine import generate_citations
        from app.retrieval.explanation_engine import generate_why_this_answer
        
        citations = generate_citations(evidence_nodes)
        why_this_answer = generate_why_this_answer(evidence_nodes)
        
        from app.swarm.agent_store import append_collaboration
        collab_id = f"col_{uuid.uuid4().hex[:8]}"
        append_collaboration({
            "collaboration_id": collab_id,
            "participants": ["planner", "retrieval", "kg", "learning", "vqa", "grounding", "critic"],
            "context": f"Swarm interaction on query: {query[:30]}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        from app.swarm.swarm_explanation_engine import compile_swarm_explanation
        explanation = compile_swarm_explanation(history)
        
        return {
            "answer": final_answer,
            "confidence": "High" if consensus_score >= 0.70 else "Medium",
            "confidence_score": consensus_score,
            "sources": citations,
            "evidence": ret_evidence,
            "why_this_answer": why_this_answer,
            "explanation": explanation,
            "swarm_history": history,
            "debug_details": {
                "steps_executed": steps,
                "contradiction_detected": contradiction,
                "consensus_fact": agreed_fact,
                "shared_memory_size": len(get_shared_memory_state())
            }
        }

swarm_manager = SwarmManager()
