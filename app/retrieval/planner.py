import uuid
from typing import List
from app.retrieval.agent_models import GoalNode, PlanNode, TaskNode

def generate_plan(goal_node: GoalNode, tasks: List[TaskNode]) -> PlanNode:
    """
    Generates a PlanNode from the GoalNode and list of decomposed TaskNodes.
    """
    # Sort tasks topologically based on dependencies or sequential execution
    ordered_steps = []
    
    # Simple dependency sorting: tasks without dependencies first, then tasks that depend on them
    remaining_tasks = list(tasks)
    added_task_ids = set()
    
    while remaining_tasks:
        progress = False
        for task in list(remaining_tasks):
            # If all dependencies are satisfied/added, we can add this task
            if all(dep_id in added_task_ids for dep_id in task.dependency_ids):
                ordered_steps.append(task.description)
                added_task_ids.add(task.task_id)
                remaining_tasks.remove(task)
                progress = True
        
        # Avoid infinite loops due to circular dependencies (if any, though none in decomposer)
        if not progress:
            for task in remaining_tasks:
                ordered_steps.append(task.description)
            break
            
    return PlanNode(
        plan_id=f"plan_{uuid.uuid4().hex[:8]}",
        goal_id=goal_node.goal_id,
        steps=ordered_steps,
        status="active"
    )
