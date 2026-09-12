import sys
import os
import json
import tempfile
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import evaluator

def test_judge_answers_score_parsing():
    cases = [
        ("100\nPerfect answer", 100),
        ("85/100\nGood answer", 85),
        ("1. 85/100\nNumbered score", 85),
        ("Q1 score: 95\nPrefix score", 95),
        ("Score: 90\nPrefix score", 90),
        ("No score here\nMissed 2 critical facts", 0),
        ("", 0),
        ("0\nCompletely wrong", 0),
    ]
    for resp, expected in cases:
        with patch('evaluator.call_llm', return_value=resp):
            scores = evaluator.judge_answers(["True ans"], ["Retrieved ans"])
            assert scores == [expected], f"Failed on {resp!r}: expected {expected}, got {scores}"

def test_retrieve_answers_iteration():
    with patch('evaluator.call_llm', return_value="Retrieved sentence."):
        rets = evaluator.retrieve_answers("{}")
        assert len(rets) == 4
        assert rets == ["Retrieved sentence."] * 4

def test_run_pipeline_error_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        valid_kg = os.path.join(tmpdir, "valid.json")
        invalid_json_kg = os.path.join(tmpdir, "invalid.json")
        missing_kg = os.path.join(tmpdir, "missing.json")
        transcript_file = os.path.join(tmpdir, "transcript.json")
        
        with open(valid_kg, "w") as f:
            json.dump({"nodes": []}, f)
        with open(invalid_json_kg, "w") as f:
            f.write("{invalid json")
        with open(transcript_file, "w") as f:
            json.dump({"text": "sample text"}, f)
            
        with patch('evaluator.call_llm') as mock_llm:
            mock_llm.side_effect = lambda prompt: "95\nGood" if "SINGLE INTEGER" in prompt else "Answer"
            results = evaluator.run_pipeline(transcript_file, [valid_kg, invalid_json_kg, missing_kg])
            assert valid_kg in results
            assert results[valid_kg] == 95.0
            assert invalid_json_kg not in results
            assert missing_kg not in results
