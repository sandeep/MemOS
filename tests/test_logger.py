import json
import pytest
from src.logger import PipelineLogger

def test_pipeline_logger(tmp_path):
    log_file = tmp_path / "runs.jsonl"
    logger = PipelineLogger("test.json", "gemma4_31b")
    
    logger.record_extraction("kg_naive", True)
    logger.record_extraction("kg_rlms", False, "Timeout Error")
    logger.record_validation("kg_naive", True)
    logger.record_scores({"kg_naive": 50.0})
    
    logger.flush(str(log_file))
    
    lines = log_file.read_text().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    
    assert data["input_file"] == "test.json"
    assert data["model"] == "gemma4_31b"
    assert data["extractions"]["kg_naive"]["status"] is True
    assert data["extractions"]["kg_rlms"]["error"] == "Timeout Error"
    assert data["validations"]["kg_naive"] is True
    assert data["scores"]["kg_naive"] == 50.0
