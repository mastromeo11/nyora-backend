import json
import re
from typing import Any, Dict, List, Optional, Tuple
from app.retrieval.agent_models import GoalNode, PlanNode, TaskNode, ToolNode, ObservationNode, ReflectionNode
from app.retrieval.tool_executor import execute_agent_tool
from app.retrieval.observation_engine import generate_observation
from app.retrieval.reflection_engine import detect_and_reflect
from app.retrieval.replanner import run_replanning
from app.config import MAX_AGENT_STEPS, LOW_CONFIDENCE_THRESHOLD
from app.llm.ollama_client import ollama_client

def run_react_reasoning(
    goal: GoalNode,
    plan: PlanNode,
    tasks: List[TaskNode],
    session_id: str
) -> Tuple[List[ToolNode], List[ObservationNode], List[ReflectionNode], List[Any]]:
    """
    Runs the ReAct loop (Thought -> Action -> Observation).
    Supports hybrid execution: falls back to planner-guided rule execution if LLM fails or gets malformed.
    """
    executed_tools: List[ToolNode] = []
    observations: List[ObservationNode] = []
    reflections: List[ReflectionNode] = []
    collected_evidence: List[Any] = []
    
    use_llm = True
    current_step = 0
    
    # We follow the topologically sorted tasks
    task_queue = list(tasks)
    
    while current_step < MAX_AGENT_STEPS and task_queue:
        task = task_queue.pop(0)
        
        # Check if the trace cache already solved this goal/task in step-level matching
        # If so, we can proceed.
        
        # Decide tool and inputs
        tool_name = map_task_to_tool_name(task)
        inputs = map_tool_inputs(tool_name, goal.query, session_id, collected_evidence)
        
        thought_str = ""
        action_str = ""
        
        if use_llm:
            # Try LLM-guided ReAct step
            prompt = f"""You are an autonomous RAG agent. Decide the next tool to run to solve: '{task.description}'.
Goal: {goal.goal_type} ({goal.query})
Plan Steps: {plan.steps}
Current Task: {task.description}

Available Tools:
- TextRetrievalTool: Queries PDF and DOCX documents
- OCRRetrievalTool: Queries image diagrams OCR text
- CLIPRetrievalTool: Visual semantic image search
- VisualQATool: Runs LLaVA on candidate images
- AudioRetrievalTool: Queries audio transcripts
- MemoryRetrievalTool: Queries session history
- ConsensusTool: Cross-modal consensus
- GroundingValidatorTool: Validates claims

Respond in exactly this format:
Thought: <brief reasoning explanation>
Action: <tool_name>(<inputs_dict_json>)
"""
            try:
                raw_res = ollama_client.generate_response(query=prompt, context="", allow_empty_context=True)
                # Parse LLM response
                parsed = parse_react_response(raw_res)
                if parsed:
                    thought_str, parsed_tool_name, parsed_inputs = parsed
                    # Force tool choice to match map_task_to_tool_name(task) for planned steps
                    planned_tool = map_task_to_tool_name(task)
                    tool_name = planned_tool
                    inputs.update(parsed_inputs)
                else:
                    print("[REACT Engine] LLM response format malformed. Falling back to planner-guided.")
                    use_llm = False
            except Exception as e:
                print(f"[REACT Engine] LLM call failed ({e}). Falling back to planner-guided.")
                use_llm = False
                
        if not use_llm or not thought_str:
            # Fallback: Planner-guided rule execution
            thought_str = f"Executing task based on plan: {task.description}."
            action_str = f"{tool_name}({inputs})"
            
        # Force failure simulation flags if present in goal query
        if "simulate_failure" in goal.query.lower() or "audio_fail" in goal.query.lower():
            if tool_name == "AudioRetrievalTool":
                inputs["simulate_failure"] = True

        print(f"[REACT Step {current_step+1}] Thought: {thought_str}")
        print(f"[REACT Step {current_step+1}] Action: {tool_name} with inputs {inputs}")
        
        # Execute tool
        try:
            outputs, tool_node = execute_agent_tool(tool_name, inputs)
        except Exception as e:
            # Catch exceptions and treat as failed ToolNode
            outputs = {"error": str(e)}
            tool_node = ToolNode(tool_name=tool_name, execution_time=0.0, success=False)
            
        executed_tools.append(tool_node)
        
        # Generate observation
        obs_node = generate_observation(tool_name, outputs)
        observations.append(obs_node)
        print(f"[REACT Step {current_step+1}] Observation: {obs_node.content}")
        
        # Accumulate retrieved evidence if it's a retrieval tool
        if tool_name in ["TextRetrievalTool", "OCRRetrievalTool", "CLIPRetrievalTool", "VisualQATool", "AudioRetrievalTool"]:
            if isinstance(outputs, list):
                collected_evidence.extend(outputs)
                
        # Reflection & Replanning Engine
        refl_node = detect_and_reflect(tool_node, obs_node)
        if refl_node:
            reflections.append(refl_node)
            print(f"[REACT Engine] Reflection compiled: {refl_node.reason}")
            
            # Replan fallback recovery tasks
            recovery_tasks = run_replanning(task, refl_node)
            if recovery_tasks:
                # Insert recovery tasks to the front of the queue
                task_queue = recovery_tasks + task_queue
                print(f"[REACT Engine] Replanner inserted recovery actions: {[t.description for t in recovery_tasks]}")
                
        current_step += 1
        
    return executed_tools, observations, reflections, collected_evidence

def map_task_to_tool_name(task: TaskNode) -> str:
    desc = task.description.lower()
    if "audio" in desc:
        return "AudioRetrievalTool"
    elif "visual" in desc or "clip" in desc:
        return "CLIPRetrievalTool"
    elif "vqa" in desc:
        return "VisualQATool"
    elif "ocr" in desc:
        return "OCRRetrievalTool"
    elif "text" in desc or "document" in desc:
        return "TextRetrievalTool"
    elif "memory" in desc or "history" in desc:
        return "MemoryRetrievalTool"
    elif "consensus" in desc:
        return "ConsensusTool"
    elif "summarize" in desc or "summary" in desc:
        return "SummarizerTool"
    elif "grounding" in desc or "validate" in desc:
        return "GroundingValidatorTool"
    else:
        return "TextRetrievalTool"

def map_tool_inputs(tool_name: str, query: str, session_id: str, collected_evidence: List[Any]) -> Dict[str, Any]:
    if tool_name in ["TextRetrievalTool", "OCRRetrievalTool", "CLIPRetrievalTool", "AudioRetrievalTool", "VisualQATool"]:
        return {"query": query}
    elif tool_name in ["MemoryRetrievalTool", "SummarizerTool", "EntityRetrieverTool"]:
        return {"session_id": session_id}
    elif tool_name == "ConsensusTool":
        return {"evidence": collected_evidence}
    elif tool_name == "GroundingValidatorTool":
        # GroundingValidator will be called later in pipeline or as tool
        return {"answer": "", "evidence": collected_evidence}
    else:
        return {}

def parse_react_response(raw: str) -> Optional[Tuple[str, str, dict]]:
    """
    Parses LLM output matching:
    Thought: <thought>
    Action: <tool_name>(<inputs_json>)
    """
    try:
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", raw, re.DOTALL | re.IGNORECASE)
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\((.*?)\)", raw, re.DOTALL | re.IGNORECASE)
        
        if thought_match and action_match:
            thought = thought_match.group(1).strip()
            tool = action_match.group(1).strip()
            args_str = action_match.group(2).strip()
            
            # Parse arguments
            args = {}
            if args_str:
                try:
                    args = json.loads(args_str)
                except Exception:
                    # Fallback string parameter mapping
                    args = {"query": args_str.replace('"', '').replace("'", "")}
            return thought, tool, args
    except Exception:
        pass
    return None
