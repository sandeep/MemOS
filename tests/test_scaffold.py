import os
from src.scaffold import init_directories

def test_init_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_directories()
    assert os.path.exists("data/secure/inputs")
    assert os.path.exists("data/secure/reconstituted")
    assert os.path.exists("data/working/scrubbed_inputs")
    assert os.path.exists("data/working/evaluations")
