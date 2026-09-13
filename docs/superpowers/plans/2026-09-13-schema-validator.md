# Schema Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a fast-failing schema validator to prevent malformed Knowledge Graphs from burning LLM Judge tokens.

**Architecture:** Create a standalone `src/validator.py` that validates JSON structure based on a schema identifier, and integrate it into the `run_pipeline.py` orchestrator loop.

**Tech Stack:** Python (json)

## Global Constraints
- Fails must catch `json.JSONDecodeError`, `KeyError`, and `TypeError`.

---

### Task 1: Create `src/validator.py`

**Files:**
- Create: `src/validator.py`
- Create: `tests/test_validator.py`

**Interfaces:**
- Produces: `validate_schema(kg_path: str, expected_schema: str) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validator.py
import os
import json
from src.validator import validate_schema

def test_validate_schema_valid_v2(tmp_path):
    kg_file = tmp_path / "valid.json"
    kg_file.write_text(json.dumps({
        "Semantic": [{"subject": "A", "relation": "B", "object": "C"}],
        "Episodic": [{"step": 1, "subject": "A", "relation": "B", "object": "C"}],
        "Procedural": [],
        "Active": []
    }))
    assert validate_schema(str(kg_file), "propositional_v2") is True

def test_validate_schema_invalid_json(tmp_path):
    kg_file = tmp_path / "invalid.json"
    kg_file.write_text("not json")
    assert validate_schema(str(kg_file), "propositional_v2") is False

def test_validate_schema_missing_keys(tmp_path):
    kg_file = tmp_path / "missing.json"
    kg_file.write_text(json.dumps({"Semantic": []}))
    assert validate_schema(str(kg_file), "propositional_v2") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_validator.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write minimal implementation**

```python
# src/validator.py
import json

def validate_schema(kg_path: str, expected_schema: str) -> bool:
    try:
        with open(kg_path, 'r') as f:
            data = json.load(f)
            
        if expected_schema == "propositional_v2":
            required_keys = {"Semantic", "Episodic", "Procedural", "Active"}
            if set(data.keys()) != required_keys:
                print(f"Validation Error: Missing or extra root keys in {kg_path}")
                return False
                
            for bucket in ["Semantic", "Procedural", "Active"]:
                if not isinstance(data[bucket], list):
                    return False
                for item in data[bucket]:
                    if set(item.keys()) != {"subject", "relation", "object"}:
                        return False
            
            if not isinstance(data["Episodic"], list):
                return False
            for item in data["Episodic"]:
                if set(item.keys()) != {"step", "subject", "relation", "object"}:
                    return False
            return True
            
        return True # Default fallback for standard/naive
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Validation Error in {kg_path}: {e}")
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/validator.py tests/test_validator.py
git commit -m "feat: add robust json schema validator for propositional kg"
```

### Task 2: Integrate Validator into Orchestrator

**Files:**
- Modify: `run_pipeline.py`
- Modify: `tests/test_run_pipeline.py`

**Interfaces:**
- Consumes: `validate_schema`

- [ ] **Step 1: Write the failing test**

Modify `tests/test_run_pipeline.py` to mock `validate_schema` and assert it is called on the KGs before evaluate_file is called.

```python
# tests/test_run_pipeline.py
from unittest.mock import patch, MagicMock
from run_pipeline import run_pipeline

@patch('run_pipeline.generate_answer_key')
@patch('run_pipeline.retrieve_answers')
@patch('run_pipeline.judge_answers')
@patch('run_pipeline.validate_schema')
def test_run_pipeline_skips_invalid_schema(mock_validate, mock_judge, mock_ret, mock_gen, tmp_path):
    # Setup mock returns
    mock_gen.return_value = ["Ans"]
    mock_validate.side_effect = [False, True] # First fails, second passes
    mock_judge.return_value = [100]
    
    transcript = tmp_path / "transcript.json"
    transcript.write_text('{}')
    kg1 = tmp_path / "kg_propositional_v2_invalid.json"
    kg1.write_text('{"bad": "schema"}')
    kg2 = tmp_path / "kg_valid.json"
    kg2.write_text('{"good": "schema"}')
    
    results = run_pipeline(str(transcript), [str(kg1), str(kg2)])
    
    assert str(kg1) not in results
    assert str(kg2) in results
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run_pipeline.py -v`
Expected: FAIL 

- [ ] **Step 3: Write minimal implementation**

Modify `run_pipeline.py` to import and call the validator:
```python
# Top of file
from src.validator import validate_schema

# Inside run_pipeline loop:
        print(f"\n--- PHASE 2 & 3: EVALUATING {kg_file} ---")
        
        # Determine expected schema based on filename
        expected_schema = "propositional_v2" if "v2" in kg_file else "standard"
        if not validate_schema(kg_file, expected_schema):
            print(f"Skipping {kg_file} due to schema validation failure.")
            continue
            
        try:
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_run_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add run_pipeline.py tests/test_run_pipeline.py
git commit -m "feat: hook schema validator into orchestrator pipeline"
```
