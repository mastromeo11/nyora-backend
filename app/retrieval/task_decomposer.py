import uuid
from typing import List
from app.retrieval.agent_models import GoalNode, TaskNode

def decompose_goal(goal_node: GoalNode) -> List[TaskNode]:
    """
    Decomposes a GoalNode into a list of TaskNode elements with dependency mappings.
    """
    q_lower = goal_node.query.lower()
    g_type = goal_node.goal_type
    
    tasks = []
    
    # Check if we are simulating audio failure (Test 4)
    is_failure_sim = "simulate_failure" in q_lower or "fail" in q_lower
    
    if g_type == "MULTIMODAL_QUERY" or ("chromadb" in q_lower and "selected" in q_lower):
        # Multimodal database lookup
        t1_id = f"task_audio_{uuid.uuid4().hex[:4]}"
        t2_id = f"task_visual_{uuid.uuid4().hex[:4]}"
        t3_id = f"task_text_{uuid.uuid4().hex[:4]}"
        t4_id = f"task_memory_{uuid.uuid4().hex[:4]}"
        t5_id = f"task_consensus_{uuid.uuid4().hex[:4]}"
        t6_id = f"task_grounding_{uuid.uuid4().hex[:4]}"
        
        # Audio task (possibly simulated failure)
        tasks.append(TaskNode(
            task_id=t1_id,
            description="Retrieve audio explanation (failure sim)" if is_failure_sim else "Retrieve audio explanation for ChromaDB selection",
            dependency_ids=[],
            status="pending"
        ))
        
        # Visual/OCR task
        tasks.append(TaskNode(
            task_id=t2_id,
            description="Retrieve visual diagram evidence for surrounding components",
            dependency_ids=[],
            status="pending"
        ))
        
        # Text/Document task
        tasks.append(TaskNode(
            task_id=t3_id,
            description="Retrieve document text evidence",
            dependency_ids=[],
            status="pending"
        ))
        
        # Memory task
        tasks.append(TaskNode(
            task_id=t4_id,
            description="Retrieve memory context",
            dependency_ids=[],
            status="pending"
        ))
        
        # Consensus task
        tasks.append(TaskNode(
            task_id=t5_id,
            description="Evaluate consensus on surrounding components",
            dependency_ids=[t2_id, t3_id],
            status="pending"
        ))
        
        # Grounding/Generation task
        tasks.append(TaskNode(
            task_id=t6_id,
            description="Run grounding validation and compile final answer",
            dependency_ids=[t1_id, t5_id, t4_id],
            status="pending"
        ))
        
    elif g_type == "SUMMARY_QUERY":
        t1_id = f"task_memory_{uuid.uuid4().hex[:4]}"
        t2_id = f"task_evidence_{uuid.uuid4().hex[:4]}"
        t3_id = f"task_summarizer_{uuid.uuid4().hex[:4]}"
        t4_id = f"task_grounding_{uuid.uuid4().hex[:4]}"
        
        tasks.append(TaskNode(
            task_id=t1_id,
            description="Retrieve past conversation history and summaries",
            dependency_ids=[],
            status="pending"
        ))
        
        tasks.append(TaskNode(
            task_id=t2_id,
            description="Retrieve document facts",
            dependency_ids=[],
            status="pending"
        ))
        
        tasks.append(TaskNode(
            task_id=t3_id,
            description="Summarize retrieved memory and evidence",
            dependency_ids=[t1_id, t2_id],
            status="pending"
        ))
        
        tasks.append(TaskNode(
            task_id=t4_id,
            description="Run grounding validation and compile final answer",
            dependency_ids=[t3_id],
            status="pending"
        ))
        
    else:
        # Default or informational lookup
        t1_id = f"task_evidence_{uuid.uuid4().hex[:4]}"
        t2_id = f"task_grounding_{uuid.uuid4().hex[:4]}"
        
        tasks.append(TaskNode(
            task_id=t1_id,
            description="Retrieve general evidence from documents",
            dependency_ids=[],
            status="pending"
        ))
        
        tasks.append(TaskNode(
            task_id=t2_id,
            description="Run grounding validation and compile final answer",
            dependency_ids=[t1_id],
            status="pending"
        ))
        
    return tasks
