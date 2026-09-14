import pytest
from pydantic import ValidationError
from src.models import CognitiveGraphV1, CognitiveGraphV2

def test_v1_rejects_empty_graph():
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV1()

def test_v2_rejects_empty_graph():
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV2(semantic=[], episodic=[], procedural=[], active=[])
