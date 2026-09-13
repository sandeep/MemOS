# Test Case Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust directory structure and orchestrator script to isolate PII and automate running multiple LLM extractors side-by-side on test datasets.

**Architecture:** We are creating a three-zone directory structure (`secure`, `working/scrubbed_inputs`, and `working/evaluations`). An orchestrator script (`run_pipeline.py`) will automatically scaffold these folders, copy input files to establish the architecture, execute all three extractors, and evaluate them against a cached ground truth.

**Tech Stack:** Python 3, JSON, existing LLM scripts (`extractor.py`, `extractor_rlms.py`, `evaluator.py`).

## Global Constraints

- No PII extraction mapping logic yet; phase 1 just does a literal file copy to establish the `scrubbed_inputs` boundary.
- File naming must be strictly formatted: `kg_naive_DATE_MODEL.json`, `kg_rlms_DATE_MODEL.json`, `kg_propositional_DATE_MODEL.json`, and `leaderboard_DATE_MODEL.md`.
- Never modify the original file in the `secure/inputs/` directory.

---

### Task 1: Scaffolding Directory Initialization

**Files:**
- Create: `src/scaffold.py`
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Produces: `init_directories()`

- [ ] **Step 1: Write the failing test**

```python
import os
import shutil
from src.scaffold import init_directories

def test_init_directories(tmp_path):
    os.chdir(tmp_path)
    init_directories()
    assert os.path.exists("data/secure/inputs")
    assert os.path.exists("data/secure/reconstituted")
    assert os.path.exists("data/working/scrubbed_inputs")
    assert os.path.exists("data/working/evaluations")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scaffold.py -v`
Expected: FAIL with "ModuleNotFoundError" or "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
import os

def init_directories():
    directories = [
        "data/secure/inputs",
        "data/secure/reconstituted",
        "data/working/scrubbed_inputs",
        "data/working/evaluations"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scaffold.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/scaffold.py tests/test_scaffold.py
git commit -m "feat: setup basic directory scaffolding for test cases"
```

### Task 2: PII Passthrough & Orchestrator CLI

**Files:**
- Create: `run_pipeline.py`

**Interfaces:**
- Consumes: `init_directories()`

- [ ] **Step 1: Write the orchestrator script**

```python
import sys
import os
import shutil
import glob
from src.scaffold import init_directories

def copy_to_scrubbed(input_path: str) -> str:
    """Mock PII phase: just copy the file across the boundary."""
    filename = os.path.basename(input_path)
    scrubbed_path = os.path.join("data/working/scrubbed_inputs", filename)
    shutil.copy2(input_path, scrubbed_path)
    return scrubbed_path

def process_file(input_path: str):
    print(f"Processing {input_path}...")
    scrubbed = copy_to_scrubbed(input_path)
    # Future tasks will hook extractors here
    print(f"Scrubbed to {scrubbed}")

def main():
    init_directories()
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <file_path> or --all")
        sys.exit(1)
        
    arg = sys.argv[1]
    if arg == "--all":
        files = glob.glob("data/secure/inputs/*.json")
        for f in files:
            process_file(f)
    else:
        if os.path.exists(arg):
            process_file(arg)
        else:
            print(f"File not found: {arg}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run script to verify it copies files**

Run: `python3 run_pipeline.py data/secure/inputs/mock.json` (create a dummy mock.json first)
Expected: "Scrubbed to data/working/scrubbed_inputs/mock.json"

- [ ] **Step 3: Commit**

```bash
git add run_pipeline.py
git commit -m "feat: orchestrator CLI with passthrough PII copy"
```

### Task 3: Migrate Evaluator & Extractors to accept Dynamic Paths

**Files:**
- Modify: `src/extractor.py`
- Modify: `src/extractor_rlms.py`

- [ ] **Step 1: Modify `src/extractor.py` to accept output path**

Change the hardcoded `"output.json"` to an argument:
```python
def extract_rlm(conversation_file: str, output_file: str = "output.json"):
    # ... inside function ...
    with open(output_file, "w") as out:
        json.dump(master_graph, out, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2: extract_rlm(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1: extract_rlm(sys.argv[1])
```

- [ ] **Step 2: Modify `src/extractor_rlms.py` to accept output path**

```python
def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_rlms.json"):
    # ... inside function ...
    # Ensure RLM writes to output_file instead of hardcoded
    base_prompt = base_prompt.replace("'output_rlms.json'", f"'{output_file}'")
```

- [ ] **Step 3: Commit**

```bash
git add src/extractor.py src/extractor_rlms.py
git commit -m "feat: parameterize extractor output paths"
```

### Task 4: Hook Extractors and Evaluator into Orchestrator

**Files:**
- Modify: `run_pipeline.py`

- [ ] **Step 1: Hook the modules into `process_file`**

```python
import datetime
from src.extractor import extract_rlm
from src.extractor_rlms import extract
from src.evaluator import run_pipeline as evaluate_pipeline

def process_file(input_path: str):
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]
    eval_dir = os.path.join("data/working/evaluations", base_name)
    os.makedirs(eval_dir, exist_ok=True)
    
    scrubbed = copy_to_scrubbed(input_path)
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    model_str = "gemma4_31b" # Defaulting for now
    tag = f"{date_str}_{model_str}"
    
    kg_naive = os.path.join(eval_dir, f"kg_naive_{tag}.json")
    kg_rlms = os.path.join(eval_dir, f"kg_rlms_{tag}.json")
    kg_prop = os.path.join(eval_dir, f"kg_propositional_{tag}.json")
    leaderboard = os.path.join(eval_dir, f"leaderboard_{tag}.md")
    
    # 1. Extract
    extract_rlm(scrubbed, kg_naive)
    extract(scrubbed, None, kg_rlms)
    extract(scrubbed, "src/prompts/propositional_kg.txt", kg_prop)
    
    # 2. Evaluate
    # Temporarily cd into eval_dir so answer_key.json gets saved correctly
    original_cwd = os.getcwd()
    os.chdir(eval_dir)
    results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), 
                                [os.path.basename(kg_naive), os.path.basename(kg_rlms), os.path.basename(kg_prop)])
    
    # 3. Write leaderboard
    with open(os.path.basename(leaderboard), "w") as f:
        f.write(f"# Leaderboard for {base_name} ({tag})\n\n")
        for k, v in results.items():
            f.write(f"- {k}: {v}%\n")
            
    os.chdir(original_cwd)
    print(f"Finished {base_name}. Leaderboard at {leaderboard}")
```

- [ ] **Step 2: Commit**

```bash
git add run_pipeline.py
git commit -m "feat: hook extraction and evaluation into orchestrator"
```
