import json
import os
from datetime import datetime

class PipelineLogger:
    def __init__(self, input_file: str, model: str):
        self.state = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_file": input_file,
            "model": model,
            "extractions": {},
            "validations": {},
            "scores": {},
            "reconstitution": None
        }

    def record_extraction(self, kg_name: str, status: bool, error: str = None, repaired: bool = False):
        self.state["extractions"][kg_name] = {"status": status, "error": error, "repaired": repaired}

    def record_validation(self, kg_name: str, status: bool):
        self.state["validations"][kg_name] = status

    def record_scores(self, scores: dict):
        self.state["scores"] = scores

    def record_eval_error(self, error: str):
        self.state["eval_error"] = error

    def record_reconstitution(self, status: bool, error: str = None):
        self.state["reconstitution"] = {"status": status, "error": error}

    def flush(self, filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.state) + "\n")
