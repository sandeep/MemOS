# Error Instrumentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Instrument the pipeline to explicitly capture RLM execution crashes, reject empty graphs during validation, and log failures comprehensively instead of swallowing them.

**Architecture:** We will wrap the RLM extraction in a try-except block that logs exact tracebacks. We will add a root validator to the Pydantic models to ensure the graph isn't entirely empty. We will add a unified logging mechanism for the pipeline.

**Tech Stack:** Python, Pydantic

## Global Constraints

- Do not use axios.
- Follow TDD: Write local pytest unit tests before touching Podman.
- STRICT PR-ONLY WORKFLOW: Never merge to main.

---

### Task 1: Add Graph Emptiness Validation

**Files:**
- Modify: `src/models.py`
- Test: `tests/test_models.py` (Create)

**Interfaces:**
- Consumes: `CognitiveGraphV1`, `CognitiveGraphV2` definitions
- Produces: Models that raise `ValueError` if all constituent lists (`nodes`/`edges` or `semantic`/`episodic`) are empty.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from src.models import CognitiveGraphV1, CognitiveGraphV2

def test_v1_rejects_empty_graph():
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV1()

def test_v2_rejects_empty_graph():
    with pytest.raises(ValidationError, match="Graph cannot be completely empty"):
        CognitiveGraphV2(semantic=[], episodic=[], procedural=[], active=[])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL (Did not raise ValidationError)

- [ ] **Step 3: Write minimal implementation**

```python
# In src/models.py, import model_validator
from pydantic import BaseModel, Field, AliasChoices, model_validator

# Add to CognitiveGraphV2:
    @model_validator(mode='after')
    def check_not_empty(self):
        if not self.semantic and not self.episodic and not self.procedural and not self.active:
            raise ValueError("Graph cannot be completely empty")
        return self

# Add to CognitiveGraphV1:
    @model_validator(mode='after')
    def check_not_empty(self):
        v1 = self.semantic_memory
        v2 = self.episodic_ledger
        v3 = self.procedural_memory
        v4 = self.active_state
        if not v1.nodes and not v1.edges and not v2.events and not v2.decisions and not v3.instructions and not v4.current_goal:
            raise ValueError("Graph cannot be completely empty")
        return self
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models.py src/models.py
git commit -m "feat(models): reject completely empty knowledge graphs"
```

### Task 2: Surface RLM Execution Errors

**Files:**
- Modify: `src/extractor_rlms.py`
- Test: `tests/test_extractor_rlms_fallback.py`

**Interfaces:**
- Consumes: `rlm.completion`
- Produces: Explicit `RuntimeError` if RLM crashes, rather than silent fallback.

- [ ] **Step 1: Write the failing test**

```python
# In tests/test_extractor_rlms_fallback.py
def test_extract_raises_on_rlm_crash(mock_rlm_class, tmp_path):
    mock_rlm_instance = mock_rlm_class.return_value
    mock_rlm_instance.completion.side_effect = Exception("RLM Internal Crash")
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{"text": "test"}')
    
    from src.extractor_rlms import extract
    with pytest.raises(RuntimeError, match="RLM Execution Failed: RLM Internal Crash"):
        extract(str(transcript_file), None, str(tmp_path / "out.json"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_extractor_rlms_fallback.py::test_extract_raises_on_rlm_crash -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# In src/extractor_rlms.py
    print("Running RLM completion...")
    try:
        response = rlm.completion(prompt)
    except Exception as e:
        raise RuntimeError(f"RLM Execution Failed: {e}") from e
    print("RLM Execution complete.")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_extractor_rlms_fallback.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_extractor_rlms_fallback.py src/extractor_rlms.py
git commit -m "feat(extractor): surface RLM execution crashes explicitly"
```
