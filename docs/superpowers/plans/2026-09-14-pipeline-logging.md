# Pipeline Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Instrument the pipeline with a JSONL audit log to provide permanent visibility into the success, failure, and scoring of each run.

**Architecture:** We will create a `PipelineLogger` class that accumulates execution state (extraction errors, validation results, evaluator scores) throughout `process_file` and flushes a complete JSON object to `data/working/pipeline_runs.jsonl` at the end of each file run.

**Tech Stack:** Python, JSON lines

## Global Constraints

- Do not use axios.
- Follow TDD: Write local pytest unit tests before touching Podman.
- STRICT PR-ONLY WORKFLOW: Never merge to main.

---

### Task 1: Create PipelineLogger utility

**Files:**
- Create: `src/logger.py`
- Create: `tests/test_logger.py`

**Interfaces:**
- Consumes: JSON file I/O
- Produces: `PipelineLogger` class with methods `record_extraction(kg_name, status, error=None)`, `record_validation(kg_name, status)`, `record_scores(scores)`, `flush(filepath)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_logger.py
import json
import pytest
from src.logger import PipelineLogger

def test_pipeline_logger(tmp_path):
    log_file = tmp_path / "runs.jsonl"
    logger = PipelineLogger("test.json", "gemma4_31b")
    
    logger.record_extraction("kg_naive", True)
    logger.record_extraction("kg_rlms", False, "Timeout Error")
    logger.record_validation("kg_naive", True)
    logger.record_scores({"kg_naive": 50.0})
    
    logger.flush(str(log_file))
    
    lines = log_file.read_text().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    
    assert data["input_file"] == "test.json"
    assert data["model"] == "gemma4_31b"
    assert data["extractions"]["kg_naive"]["status"] is True
    assert data["extractions"]["kg_rlms"]["error"] == "Timeout Error"
    assert data["validations"]["kg_naive"] is True
    assert data["scores"]["kg_naive"] == 50.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_logger.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/logger.py
import json
import os
from datetime import datetime

class PipelineLogger:
    def __init__(self, input_file: str, model: str):
        self.state = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_file": input_file,
            "model": model,
            "extractions": {},
            "validations": {},
            "scores": {},
            "reconstitution": None
        }

    def record_extraction(self, kg_name: str, status: bool, error: str = None):
        self.state["extractions"][kg_name] = {"status": status, "error": error}

    def record_validation(self, kg_name: str, status: bool):
        self.state["validations"][kg_name] = status

    def record_scores(self, scores: dict):
        self.state["scores"] = scores

    def record_reconstitution(self, status: bool, error: str = None):
        self.state["reconstitution"] = {"status": status, "error": error}

    def flush(self, filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.state) + "\n")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_logger.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_logger.py src/logger.py
git commit -m "feat(pipeline): create PipelineLogger utility"
```

### Task 2: Integrate PipelineLogger into `run_pipeline.py`

**Files:**
- Modify: `run_pipeline.py`

**Interfaces:**
- Consumes: `PipelineLogger`
- Produces: Integrated try/except blocks around extractions and validations to populate the logger state.

- [ ] **Step 1: Write minimal implementation**

```python
# Update run_pipeline.py
# 1. Add import:
from src.logger import PipelineLogger
import traceback

# 2. Inside process_file, initialize logger:
    logger = PipelineLogger(input_path, model_str)
    log_file = os.path.join("data", "working", "pipeline_runs.jsonl")
    
# 3. Wrap extractions:
    # 1. Extract
    extractions = [
        ("kg_naive", kg_naive, lambda: extract_rlm(scrubbed, kg_naive)),
        ("kg_rlms", kg_rlms, lambda: extract(scrubbed, None, kg_rlms)),
        ("kg_prop", kg_prop, lambda: extract(scrubbed, "src/prompts/propositional_kg.txt", kg_prop)),
        ("kg_prop_v2", kg_prop_v2, lambda: extract(scrubbed, "src/prompts/propositional_v2_kg.txt", kg_prop_v2))
    ]
    
    for name, path, func in extractions:
        try:
            func()
            logger.record_extraction(name, True)
        except Exception as e:
            logger.record_extraction(name, False, str(e))
            print(f"Extraction failed for {name}: {e}")

# 4. Wrap validations:
        valid_kgs = []
        for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2]:
            kg_base = os.path.basename(kg)
            if kg == kg_naive:
                valid_kgs.append(kg_base)
                logger.record_validation("kg_naive", True)
                continue
                
            schema = "propositional_v2" if kg == kg_prop_v2 else "standard"
            try:
                is_valid = validate_schema(os.path.join(original_cwd, kg), schema)
                if is_valid:
                    valid_kgs.append(kg_base)
                logger.record_validation(kg_base, is_valid)
            except Exception as e:
                logger.record_validation(kg_base, False)
                print(f"Validation crashed for {kg_base}: {e}")

# 5. Record scores and flush:
        results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), valid_kgs)
        logger.record_scores(results)
# 6. Reconstitution block:
    try:
        reconstitute(kg_prop, reconstituted_file)
        logger.record_reconstitution(True)
        print(f"Reconstituted KG to {reconstituted_file}")
    except Exception as e:
        logger.record_reconstitution(False, str(e))
        print(f"Skipping reconstitution for {base_name}: {e}")
        
    logger.flush(log_file)
```

- [ ] **Step 2: Run script to verify it works without breaking**

Run: `python3 -m py_compile run_pipeline.py`
Expected: PASS (No syntax errors)

- [ ] **Step 3: Commit**

```bash
git add run_pipeline.py
git commit -m "feat(pipeline): integrate PipelineLogger into run_pipeline.py"
```
