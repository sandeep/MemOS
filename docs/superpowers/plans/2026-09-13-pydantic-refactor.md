# Pydantic Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce Pydantic models to strictly normalize and validate all Knowledge Graph LLM outputs (both V1 and V2), and ensure the extractor correctly catches agent outputs that miss the file system.

**Architecture:** 
- Define Pydantic models for both the V1 (Legacy) and V2 (Propositional) schemas in a new `src/models.py`.
- Update `src/validator.py` to parse the raw text through Pydantic, instantly coercing casing issues and stripping out CoT (Chain of Thought) text, then saving the normalized JSON back to disk.
- Update `src/extractor_rlms.py` to capture the raw RLM agent output and feed it to the validator if the file wasn't natively created.
- Add `pydantic` to the `Containerfile`.

**Tech Stack:** Python, Pydantic, Podman

## Global Constraints
- `pydantic` must be added to `Containerfile`.
- Normalized JSON must be dumped back to disk so `src/evaluator.py` can read it cleanly.

---

### Task 1: Update Dependencies

**Files:**
- Modify: `Containerfile`

- [ ] **Step 1: Add Pydantic to Containerfile**

Modify `Containerfile` to include `pydantic` in the pip install command:
```dockerfile
RUN pip install --no-cache-dir requests presidio-analyzer presidio-anonymizer rlms openai pydantic
```

- [ ] **Step 2: Commit**

```bash
git add Containerfile
git commit -m "build: add pydantic dependency"
```

### Task 2: Define Data Models

**Files:**
- Create: `src/models.py`

**Interfaces:**
- Produces: `CognitiveGraphV2`, `CognitiveGraphV1`

- [ ] **Step 1: Write implementation**

Create `src/models.py`:
```python
from pydantic import BaseModel, Field, AliasChoices
from typing import List, Dict, Any, Optional

# --- V2 (Propositional) Models ---
class Triple(BaseModel):
    subject: str
    relation: str
    object: str

class EpisodicTriple(Triple):
    step: int

class CognitiveGraphV2(BaseModel):
    # AliasChoices allows matching either TitleCase or lowercase keys from the LLM
    semantic: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Semantic', 'semantic'))
    episodic: List[EpisodicTriple] = Field(default_factory=list, validation_alias=AliasChoices('Episodic', 'episodic'))
    procedural: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Procedural', 'procedural'))
    active: List[Triple] = Field(default_factory=list, validation_alias=AliasChoices('Active', 'active'))

# --- V1 (Legacy/Naive) Models ---
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

- [ ] **Step 2: Commit**

```bash
git add src/models.py
git commit -m "feat: introduce pydantic schemas for v1 and v2 knowledge graphs"
```

### Task 3: Rewrite Validator

**Files:**
- Modify: `src/validator.py`

**Interfaces:**
- Consumes: `CognitiveGraphV1`, `CognitiveGraphV2`

- [ ] **Step 1: Write implementation**

Rewrite `src/validator.py` to use Pydantic. If validation passes, dump the normalized model back to the file so it has perfectly clean casing/structure.

```python
import json
import re
from pydantic import ValidationError
from src.models import CognitiveGraphV1, CognitiveGraphV2

def extract_json_block(text: str) -> str:
    # Attempt to extract JSON from markdown or raw text
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match: return match.group(0).strip()
    return text

def validate_and_normalize(raw_text: str, expected_schema: str) -> str:
    """Validates raw text against schema and returns normalized JSON string. Raises ValueError if invalid."""
    clean_json = extract_json_block(raw_text)
    
    try:
        if expected_schema == "propositional_v2":
            model = CognitiveGraphV2.model_validate_json(clean_json)
        else:
            model = CognitiveGraphV1.model_validate_json(clean_json)
            
        # Return perfectly normalized JSON (keys will match the Pydantic field names, e.g., 'semantic' instead of 'Semantic')
        return model.model_dump_json(indent=2)
    except ValidationError as e:
        raise ValueError(f"Pydantic Validation Error: {e}")

def validate_schema(kg_path: str, expected_schema: str) -> bool:
    try:
        with open(kg_path, 'r') as f:
            raw_text = f.read()
            
        normalized_json = validate_and_normalize(raw_text, expected_schema)
        
        # Overwrite the file with the pristine, normalized JSON
        with open(kg_path, 'w') as f:
            f.write(normalized_json)
            
        return True
    except (FileNotFoundError, ValueError) as e:
        print(f"Validation Error in {kg_path}: {e}")
        return False
```

- [ ] **Step 2: Commit**

```bash
git add src/validator.py
git commit -m "feat: use pydantic for robust validation and normalization"
```

### Task 4: Catch Missing Files in Orchestrator

**Files:**
- Modify: `run_pipeline.py`
- Modify: `src/extractor_rlms.py`

**Interfaces:**
- Modifies orchestrator to handle agents returning JSON in stdout rather than writing to file.

- [ ] **Step 1: Write implementation for `extractor_rlms.py`**

Modify `src/extractor_rlms.py` to return the response text from `rlm.completion()`.
Change:
```python
    print("Running RLM completion...")
    response = rlm.completion(prompt)
    print("RLM Execution complete.")
    
    # NEW: Write the raw response to the file if it doesn't exist so the validator can pick it up
    if not os.path.exists(output_file) and response:
        with open(output_file, 'w') as f:
            f.write(response)
```

- [ ] **Step 2: Commit**

```bash
git add src/extractor_rlms.py
git commit -m "fix: ensure rlm agent output is saved to disk if agent skips file writing"
```
