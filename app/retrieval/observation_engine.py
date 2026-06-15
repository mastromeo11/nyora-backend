import uuid
from datetime import datetime
from typing import Any
from app.retrieval.agent_models import ObservationNode
from app.retrieval.evidence_models import EvidenceNode

def generate_observation(tool_name: str, outputs: Any) -> ObservationNode:
    """
    Analyzes tool execution results and constructs a descriptive ObservationNode.
    """
    timestamp = datetime.utcnow().isoformat()
    obs_id = f"obs_{uuid.uuid4().hex[:8]}"
    
    if isinstance(outputs, dict) and "error" in outputs:
        content = f"Tool {tool_name} execution failed with error: {outputs['error']}"
    elif tool_name in ["TextRetrievalTool", "OCRRetrievalTool", "AudioRetrievalTool"]:
        # Outputs should be List[EvidenceNode]
        if not outputs:
            content = f"{tool_name} returned no evidence."
        else:
            sources = sorted(list({node.source for node in outputs if hasattr(node, "source")}))
            content = f"{tool_name} successfully retrieved {len(outputs)} evidence nodes from sources: {', '.join(sources)}."
    elif tool_name == "CLIPRetrievalTool":
        if not outputs:
            content = "CLIPRetrievalTool returned no image matches."
        else:
            sources = sorted(list({node.source for node in outputs}))
            content = f"CLIPRetrievalTool matched {len(outputs)} visual segments from files: {', '.join(sources)}."
    elif tool_name == "VisualQATool":
        if not outputs:
            content = "VisualQATool returned no answers."
        else:
            content = f"VisualQATool successfully completed. Found answers: {'; '.join([n.content for n in outputs])}."
    elif tool_name == "MemoryRetrievalTool":
        if not outputs:
            content = "MemoryRetrievalTool found no active session history."
        else:
            content = f"MemoryRetrievalTool successfully loaded {len(outputs)} conversational turns and preferences."
    elif tool_name == "ConsensusTool":
        score = outputs.get("consensus_score", 0.0)
        mods = outputs.get("supporting_modalities", [])
        content = f"Consensus evaluation complete with score {score:.2f} supported by modalities: {', '.join(mods)}."
    elif tool_name == "GroundingValidatorTool":
        claim_status = outputs.get("grounding_report", [])
        content = f"Grounding validation verified generated response. Found {len(claim_status)} grounded claims."
    elif tool_name == "SummarizerTool":
        content = "SummarizerTool processed conversation logs and compiled long-term session summary."
    elif tool_name == "EntityRetrieverTool":
        focus = outputs.get("current_entity_focus", "None")
        content = f"Active entity focus resolved to: '{focus}'."
    else:
        content = f"Tool {tool_name} completed execution."
        
    return ObservationNode(
        observation_id=obs_id,
        tool_name=tool_name,
        content=content,
        timestamp=timestamp
    )
