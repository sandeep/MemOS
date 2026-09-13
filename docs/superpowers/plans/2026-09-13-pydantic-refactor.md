# Pydantic Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce Pydantic models to strictly normalize and validate all Knowledge Graph LLM outputs (both V1 and V2), and ensure the extractor correctly catches agent outputs that miss the file system.

**Architecture:** 
- Define Pydantic models for both the V1 (Legacy) and V2 (Propositional) schemas in `src/models.py`.
- Update `src/validator.py` to parse the raw text through Pydantic, instantly coercing casing issues and stripping out CoT text, then saving the normalized JSON back to disk.
- Update `src/extractor_rlms.py` to capture the raw RLM agent output and feed it to the validator if the file wasn't natively created.

**Tech Stack:** Python, Pydantic, Podman

---

### Task 1: Update Dependencies

**Files:**
- Modify: `Containerfile`
- Modify: `tests/test_imports.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_imports.py
def test_pydantic_installed():
    try:
        import pydantic
        assert True
    except ImportError:
        assert False, "Pydantic is not installed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_imports.py -v`
Expected: FAIL with "ImportError" or similar

- [ ] **Step 3: Write minimal implementation**

Modify `Containerfile`:
```dockerfile
RUN pip install --no-cache-dir requests presidio-analyzer presidio-anonymizer rlms openai pydantic
```

- [ ] **Step 4: Run test to verify it passes**

Run: `podman build -t braindrain . && podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_imports.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Containerfile tests/test_imports.py
git commit -m "build: add pydantic dependency to containerfile"
```

### Task 2: Define Data Models

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from src.models import CognitiveGraphV2, CognitiveGraphV1
import json

def test_v2_alias_coercion():
    # Test that lowercase keys from LLM are coerced to the correct Pydantic fields
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.models'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/models.py
from pydantic import BaseModel, Field, AliasChoices
from typing import List, Dict, Any

class Triple(BaseModel):
    subject: str
    relation: str
    object: str

class EpisodicTriple(Triple):
    step: int

class CognitiveGraphV2(BaseModel):
    semantic: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Semantic', 'semantic'))
    episodic: List[EpisodicTriple] = Field(default_factory=list, validation_alias=AliasChoices('Episodic', 'episodic'))
    procedural: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Procedural', 'procedural'))
    active: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Active', 'active'))

class SemanticMemoryV1(BaseModel):
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)

class EpisodicLedgerV1(BaseModel):
    events: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    rejected_branches: List[Dict[str, Any]] = Field(default_factory=list)

class ProceduralMemoryV1(BaseModel):
    instructions: List[Dict[str, Any]] = Field(default_factory=list)

class ActiveStateV1(BaseModel):
    current_goal: str = ""
    blockers: List[str] = Field(default_factory=list)
    next_action: str = ""

class CognitiveGraphV1(BaseModel):
    semantic_memory: SemanticMemoryV1 = Field(default_factory=SemanticMemoryV1)
    episodic_ledger: EpisodicLedgerV1 = Field(default_factory=EpisodicLedgerV1)
    procedural_memory: ProceduralMemoryV1 = Field(default_factory=ProceduralMemoryV1)
    active_state: ActiveStateV1 = Field(default_factory=ActiveStateV1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: introduce pydantic schemas for v1 and v2 knowledge graphs"
```

### Task 3: Rewrite Validator

**Files:**
- Modify: `src/validator.py`
- Modify: `tests/test_validator.py`

- [ ] **Step 1: Write the failing test**

Modify `tests/test_validator.py` to assert that the file is overwritten with normalized JSON:
```python
# tests/test_validator.py
import json
from src.validator import validate_schema

def test_validate_schema_normalizes_casing(tmp_path):
    kg_file = tmp_path / "valid.json"
    # Provide lowercase keys which are technically invalid under the old schema but coercible by Pydantic
    kg_file.write_text(json.dumps({
        "semantic": [{"subject": "A", "relation": "B", "object": "C"}],
        "episodic": [{"step": 1, "subject": "A", "relation": "B", "object": "C"}],
        "procedural": [],
        "active": []
    }))
    assert validate_schema(str(kg_file), "propositional_v2") is True
    
    # Assert it was overwritten with Pydantic's dumped fields (which are lowercase anyway, but normalized)
    normalized = json.loads(kg_file.read_text())
    assert "semantic" in normalized
    assert isinstance(normalized["semantic"], list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_validator.py -v`
Expected: FAIL (because old validator expects exact `Semantic` root keys)

- [ ] **Step 3: Write minimal implementation**

```python
# src/validator.py
import re
from pydantic import ValidationError
from src.models import CognitiveGraphV1, CognitiveGraphV2

def extract_json_block(text: str) -> str:
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match: return match.group(0).strip()
    return text

def validate_and_normalize(raw_text: str, expected_schema: str) -> str:
    clean_json = extract_json_block(raw_text)
    try:
        if expected_schema == "propositional_v2":
            model = CognitiveGraphV2.model_validate_json(clean_json)
        else:
            model = CognitiveGraphV1.model_validate_json(clean_json)
        return model.model_dump_json(indent=2)
    except ValidationError as e:
        raise ValueError(f"Pydantic Validation Error: {e}")

def validate_schema(kg_path: str, expected_schema: str) -> bool:
    try:
        with open(kg_path, 'r') as f:
            raw_text = f.read()
            
        normalized_json = validate_and_normalize(raw_text, expected_schema)
        
        with open(kg_path, 'w') as f:
            f.write(normalized_json)
            
        return True
    except (FileNotFoundError, ValueError) as e:
        print(f"Validation Error in {kg_path}: {e}")
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/validator.py tests/test_validator.py
git commit -m "feat: use pydantic for robust validation and normalization"
```

### Task 4: Catch Missing Files in Orchestrator

**Files:**
- Modify: `src/extractor_rlms.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extractor_rlms.py
import os
from unittest.mock import patch
from src.extractor_rlms import extract

@patch('src.extractor_rlms.RLM')
def test_extract_saves_stdout_fallback(mock_rlm_class, tmp_path):
    mock_rlm_instance = mock_rlm_class.return_value
    mock_rlm_instance.completion.return_value = '{"fallback": "json"}'
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{}')
    output_file = tmp_path / "out.json"
    
    # Run extract, which should see output_file doesn't exist and save the response
    extract(str(transcript_file), None, str(output_file))
    
    assert output_file.exists()
    assert output_file.read_text() == '{"fallback": "json"}'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_extractor_rlms.py -v`
Expected: FAIL 

- [ ] **Step 3: Write minimal implementation**

Modify `src/extractor_rlms.py` around line 43:
```python
    print("Running RLM completion...")
    response = rlm.completion(prompt)
    print("RLM Execution complete.")
    
    if not os.path.exists(output_file) and response:
        print(f"Agent did not create {output_file}. Saving raw stdout fallback...")
        with open(output_file, 'w') as f:
            f.write(response)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `podman run --rm -v $(pwd):/app braindrain python -m pytest tests/test_extractor_rlms.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/extractor_rlms.py tests/test_extractor_rlms.py
git commit -m "fix: ensure rlm agent output is saved to disk if agent skips file writing"
```
