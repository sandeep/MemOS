import sys
import os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import json
import pytest
from unittest.mock import patch
from src.evaluator import run_pipeline

@patch('src.evaluator.call_llm')
def test_evaluator_saves_data_to_disk(mock_call_llm, tmp_path):
    def mock_llm_response(prompt, *args, **kwargs):
        if "generate" in prompt.lower() or "synthesize" in prompt.lower() or "attempt" in prompt.lower():
            return "Mock Ground Truth Answer."
        if "Knowledge Graph" in prompt:
            return "Mock Retrieved Answer."
        return "100\nMock Explanation."
        
    mock_call_llm.side_effect = mock_llm_response
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{"text": "mock transcript"}')
    
    kg_file = tmp_path / "mock_kg.json"
    kg_file.write_text('{"nodes": [], "edges": []}')
    
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        results = run_pipeline(str(transcript_file), [str(kg_file)])
    finally:
        os.chdir(original_cwd)
        
    assert str(kg_file) in results
    assert results[str(kg_file)] == 100.0
    
    assert (tmp_path / "answer_key.json").exists()
    assert (tmp_path / "mock_kg_retrieved.json").exists()
    assert (tmp_path / "mock_kg_scores.json").exists()
