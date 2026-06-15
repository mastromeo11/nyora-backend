import uuid
from typing import List
from app.retrieval.agent_models import TaskNode, ReflectionNode
from app.config import MAX_REPLANNING_STEPS

# Global replan step counter in-memory
_replan_steps_count = 0

def reset_replanner_count():
    global _replan_steps_count
    _replan_steps_count = 0

def run_replanning(failed_task: TaskNode, reflection: ReflectionNode) -> List[TaskNode]:
    """
    Generates fallback/recovery tasks based on the failure reflection.
    """
    global _replan_steps_count
    
    if _replan_steps_count >= MAX_REPLANNING_STEPS:
        print(f"[REPLANNER] Maximum replanning step limit ({MAX_REPLANNING_STEPS}) reached. Skipping replan.")
        return []
        
    _replan_steps_count += 1
    recovery_tasks = []
    
    desc_lower = failed_task.description.lower()
    
    # 1. Audio retrieval fails -> fallback to text and OCR retrieval
    if "audio" in desc_lower:
        print("[REPLANNER] Audio retrieval failed. Triggering fallback to Document Text and OCR retrieval.")
        t1 = TaskNode(
            task_id=f"recovery_text_{uuid.uuid4().hex[:4]}",
            description="Fallback: Retrieve document text evidence for ChromaDB selection",
            dependency_ids=[],
            status="pending"
        )
        t2 = TaskNode(
            task_id=f"recovery_ocr_{uuid.uuid4().hex[:4]}",
            description="Fallback: Retrieve OCR diagram evidence for ChromaDB selection",
            dependency_ids=[],
            status="pending"
        )
        recovery_tasks.extend([t1, t2])
        
    # 2. Visual QA fails -> fallback to caption and OCR
    elif "vqa" in desc_lower or "visual" in desc_lower:
        print("[REPLANNER] Visual reasoning failed. Triggering fallback to OCR and cached image caption search.")
        t1 = TaskNode(
            task_id=f"recovery_ocr_{uuid.uuid4().hex[:4]}",
            description="Fallback: Retrieve OCR diagram evidence",
            dependency_ids=[],
            status="pending"
        )
        recovery_tasks.append(t1)
        
    # 3. Memory retrieval fails -> skip memory
    elif "memory" in desc_lower:
        print("[REPLANNER] Memory retrieval failed. Skipping memory dependencies.")
        
    return recovery_tasks
