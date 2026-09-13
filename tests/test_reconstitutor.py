import os
import json
import pytest
from src.reconstitutor import reconstitute, create_latest_symlink

def test_create_latest_symlink_new(tmp_path):
    target_file = tmp_path / "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    target_file.write_text('{"entities": ["alpha"]}')
    
    symlink_path = create_latest_symlink(str(target_file))
    
    assert os.path.islink(symlink_path)
    assert os.readlink(symlink_path) == "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    with open(symlink_path, "r") as f:
        data = json.load(f)
    assert data == {"entities": ["alpha"]}

def test_create_latest_symlink_update_existing(tmp_path):
    file1 = tmp_path / "kg_propositional_2026-09-12_gemma4_31b_reconstituted.json"
    file1.write_text('{"version": 1}')
    create_latest_symlink(str(file1))
    
    symlink_path = tmp_path / "latest.json"
    assert os.path.islink(symlink_path)
    assert os.readlink(str(symlink_path)) == "kg_propositional_2026-09-12_gemma4_31b_reconstituted.json"
    
    file2 = tmp_path / "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    file2.write_text('{"version": 2}')
    create_latest_symlink(str(file2))
    
    assert os.path.islink(symlink_path)
    assert os.readlink(str(symlink_path)) == "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    with open(symlink_path, "r") as f:
        data = json.load(f)
    assert data == {"version": 2}

def test_reconstitute_copies_and_symlinks(tmp_path):
    source_kg = tmp_path / "working" / "kg_prop.json"
    source_kg.parent.mkdir(parents=True, exist_ok=True)
    source_kg.write_text('{"graph": "test"}')
    
    target_kg = tmp_path / "secure" / "reconstituted" / "sample" / "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    
    result = reconstitute(str(source_kg), str(target_kg))
    
    assert result == str(target_kg)
    assert os.path.exists(target_kg)
    with open(target_kg, "r") as f:
        assert json.load(f) == {"graph": "test"}
        
    latest_symlink = tmp_path / "secure" / "reconstituted" / "sample" / "latest.json"
    assert os.path.islink(str(latest_symlink))
    assert os.readlink(str(latest_symlink)) == "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"

def test_reconstitute_handles_missing_source(tmp_path):
    missing_source = tmp_path / "nonexistent.json"
    target_kg = tmp_path / "secure" / "reconstituted" / "sample" / "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
    
    result = reconstitute(str(missing_source), str(target_kg))
    
    assert result == str(target_kg)
    assert os.path.exists(target_kg)
    with open(target_kg, "r") as f:
        assert json.load(f) == {}
        
    latest_symlink = tmp_path / "secure" / "reconstituted" / "sample" / "latest.json"
    assert os.path.islink(str(latest_symlink))
    assert os.readlink(str(latest_symlink)) == "kg_propositional_2026-09-13_gemma4_31b_reconstituted.json"
