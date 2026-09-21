from src.models import CognitiveGraphV2, CognitiveGraphV1
import json
import pytest

def test_v2_alias_coercion():
    raw = {
        "semantic": [{"subject": "A", "relation": "B", "object": "C"}],
        "episodic": [{"step": 1, "subject": "A", "relation": "B", "object": "C"}],
        "procedural": [],
        "active": []
    }
    model = CognitiveGraphV2.model_validate(raw)
    assert len(model.semantic) == 1
    assert model.episodic[0].step == 1

def test_v1_legacy_parsing():
    raw = {
        "semantic_memory": {"nodes": [{"id": "1"}], "edges": []},
        "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
        "procedural_memory": {"instructions": []},
        "active_state": {"current_goal": "test", "blockers": [], "next_action": ""}
    }
    model = CognitiveGraphV1.model_validate(raw)
    assert len(model.semantic_memory.nodes) == 1

def test_v1_rejects_empty_graph():
    from pydantic import ValidationError
    from src.models import CognitiveGraphV1
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV1()

def test_v2_rejects_empty_graph():
    from pydantic import ValidationError
    from src.models import CognitiveGraphV2
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV2(semantic=[], episodic=[], procedural=[], active=[])
