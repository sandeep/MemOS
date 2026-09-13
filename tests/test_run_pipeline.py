import os
import sys
import datetime
from unittest.mock import patch, MagicMock
import pytest
from run_pipeline import copy_to_scrubbed, process_file, main

@pytest.fixture(autouse=True)
def mock_pipeline_components(monkeypatch):
    """Mock extractor and evaluator calls by default in run_pipeline tests."""
    monkeypatch.setattr("run_pipeline.extract_rlm", lambda *a, **kw: None)
    monkeypatch.setattr("run_pipeline.extract", lambda *a, **kw: None)
    monkeypatch.setattr("run_pipeline.evaluate_pipeline", lambda *a, **kw: {"test.json": 100.0})

def test_copy_to_scrubbed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.makedirs("data/secure/inputs", exist_ok=True)
    os.makedirs("data/working/scrubbed_inputs", exist_ok=True)
    
    mock_file = "data/secure/inputs/test.json"
    with open(mock_file, "w") as f:
        f.write('{"test": 123}')
        
    result_path = copy_to_scrubbed(mock_file)
    assert result_path == "data/working/scrubbed_inputs/test.json"
    assert os.path.exists(result_path)
    with open(result_path, "r") as f:
        assert f.read() == '{"test": 123}'

def test_process_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    os.makedirs("data/secure/inputs", exist_ok=True)
    os.makedirs("data/working/scrubbed_inputs", exist_ok=True)
    
    mock_file = "data/secure/inputs/sample.json"
    with open(mock_file, "w") as f:
        f.write('{"data": "val"}')
        
    process_file(mock_file)
    captured = capsys.readouterr().out
    assert "Processing data/secure/inputs/sample.json..." in captured
    assert "Scrubbed to data/working/scrubbed_inputs/sample.json" in captured
    assert os.path.exists("data/working/scrubbed_inputs/sample.json")

def test_process_file_pipeline_orchestration(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    os.makedirs("data/secure/inputs", exist_ok=True)
    os.makedirs("data/working/scrubbed_inputs", exist_ok=True)
    
    mock_file = "data/secure/inputs/sample.json"
    with open(mock_file, "w") as f:
        f.write('{"data": "val"}')
        
    with patch("run_pipeline.extract_rlm") as mock_extract_rlm, \
         patch("run_pipeline.extract") as mock_extract, \
         patch("run_pipeline.evaluate_pipeline") as mock_evaluate:
         
        mock_evaluate.return_value = {
            "kg_naive_test.json": 80.0,
            "kg_rlms_test.json": 75.0,
            "kg_propositional_test.json": 90.0,
        }
        
        process_file(mock_file)
        
        captured = capsys.readouterr().out
        assert "Processing data/secure/inputs/sample.json..." in captured
        assert "Scrubbed to data/working/scrubbed_inputs/sample.json" in captured
        assert "Finished sample. Leaderboard at " in captured
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        tag = f"{date_str}_gemma4_31b"
        eval_dir = os.path.join("data/working/evaluations", "sample")
        expected_naive = os.path.join(eval_dir, f"kg_naive_{tag}.json")
        expected_rlms = os.path.join(eval_dir, f"kg_rlms_{tag}.json")
        expected_prop = os.path.join(eval_dir, f"kg_propositional_{tag}.json")
        expected_leaderboard = os.path.join(eval_dir, f"leaderboard_{tag}.md")
        
        scrubbed_path = "data/working/scrubbed_inputs/sample.json"
        
        # Verify extractors called
        mock_extract_rlm.assert_called_once_with(scrubbed_path, expected_naive)
        assert mock_extract.call_count == 2
        mock_extract.assert_any_call(scrubbed_path, None, expected_rlms)
        mock_extract.assert_any_call(scrubbed_path, "src/prompts/propositional_kg.txt", expected_prop)
        
        # Verify evaluator called
        mock_evaluate.assert_called_once()
        eval_call_args = mock_evaluate.call_args[0]
        assert eval_call_args[0] == os.path.join(str(tmp_path), scrubbed_path)
        assert eval_call_args[1] == [
            os.path.basename(expected_naive),
            os.path.basename(expected_rlms),
            os.path.basename(expected_prop)
        ]
        
        # Verify leaderboard file written
        assert os.path.exists(expected_leaderboard)
        with open(expected_leaderboard, "r") as f:
            content = f.read()
            assert f"# Leaderboard for sample ({tag})" in content
            assert "- kg_naive_test.json: 80.0%" in content
            assert "- kg_rlms_test.json: 75.0%" in content
            assert "- kg_propositional_test.json: 90.0%" in content
            
        # Verify cwd restored
        assert os.getcwd() == str(tmp_path)

def test_main_no_args(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr().out
    assert "Usage: python run_pipeline.py <file_path> or --all" in captured

def test_main_single_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    mock_file = "data/secure/inputs/mock.json"
    os.makedirs("data/secure/inputs", exist_ok=True)
    with open(mock_file, "w") as f:
        f.write('{"key": "value"}')

    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", mock_file])
    main()
    captured = capsys.readouterr().out
    assert f"Processing {mock_file}..." in captured
    assert "Scrubbed to data/working/scrubbed_inputs/mock.json" in captured
    assert os.path.exists("data/working/scrubbed_inputs/mock.json")

def test_main_file_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "nonexistent.json"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr().out
    assert "File not found: nonexistent.json" in captured

def test_main_all(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    os.makedirs("data/secure/inputs", exist_ok=True)
    with open("data/secure/inputs/f1.json", "w") as f:
        f.write('{"f": 1}')
    with open("data/secure/inputs/f2.json", "w") as f:
        f.write('{"f": 2}')

    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--all"])
    main()
    captured = capsys.readouterr().out
    assert "data/working/scrubbed_inputs/f1.json" in captured
    assert "data/working/scrubbed_inputs/f2.json" in captured
    assert os.path.exists("data/working/scrubbed_inputs/f1.json")
    assert os.path.exists("data/working/scrubbed_inputs/f2.json")
