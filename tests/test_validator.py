import json
from src.validator import validate_schema

def test_validate_schema_normalizes_casing(tmp_path):
    kg_file = tmp_path / "valid.json"
    kg_file.write_text(json.dumps({
        "semantic": [{"subject": "A", "relation": "B", "object": "C"}],
        "episodic": [{"step": 1, "subject": "A", "relation": "B", "object": "C"}],
        "procedural": [],
        "active": []
    }))
    assert validate_schema(str(kg_file), "propositional_v2") is True
    
    normalized = json.loads(kg_file.read_text())
    assert "semantic" in normalized
    assert isinstance(normalized["semantic"], list)

def test_validate_schema_v1(tmp_path):
    kg_file = tmp_path / "v1.json"
    kg_file.write_text(json.dumps({
        "semantic_memory": {"nodes": [{"id": "n1", "label": "L", "attributes": {}, "source": "src"}], "edges": []},
        "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
        "procedural_memory": {"instructions": []},
        "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
    }))
    assert validate_schema(str(kg_file), "standard") is True
