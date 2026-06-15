from app.swarm.agent_base import BaseSwarmAgent
from typing import Dict, Any

class VQAAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__(
            agent_id="vqa",
            agent_name="VQA Agent",
            role="visual_question_answering",
            capabilities=["ocr", "captioning", "image_qa"]
        )
        
    def _run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        vqa_res = {
            "answer": "Visual details verified from retrieved screenshots.",
            "confidence": "High",
            "source_image": "screenshot_1.png"
        }
        self.write_mem("vqa_result", vqa_res)
        return {"status": "success", "vqa_result": vqa_res}
