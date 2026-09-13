import os
import sys
import pytest
from run_pipeline import copy_to_scrubbed, process_file, main

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
    main()
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
