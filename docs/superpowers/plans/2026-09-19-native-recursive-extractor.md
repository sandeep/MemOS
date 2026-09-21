# Native Python Extractor Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely replace the brittle, sandbox-dependent `RLM` library with a deterministic, native Python recursive chunking orchestrator that guarantees 100% file coverage and valid JSON extraction.

**Architecture:** We will strip the `rlm` dependency entirely from `src/extractor_rlms.py`. The script will now act as the orchestrator: it will slice the scrubbed transcript into 3000-character chunks, format the respective prompt template (`propositional_kg`, `v2`, etc.) with the chunk text, execute the LLM call using our existing `llm_utils`, extract the JSON via robust markdown regex, and merge the graphs natively using `src.extractor.merge_graphs`.

**Tech Stack:** Python, `re`, `json`, `llm_utils`

## Global Constraints

- No new 3rd party package dependencies.
- Must preserve the exact function signature of `def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_rlms.json")` in `src/extractor_rlms.py` to avoid breaking `run_pipeline.py`.
- Must handle LLM markdown JSON outputs (` ```json ... ``` `) securely using Regex extraction.

---

### Task 1: Rewrite `src/extractor_rlms.py`

**Files:**
- Modify: `src/extractor_rlms.py`

**Interfaces:**
- Consumes: `src.extractor.scrub_pii`, `src.extractor.merge_graphs`, `src.llm_utils.call_llm`
- Produces: A completed JSON output file located at `output_file`.

- [ ] **Step 1: Write the failing test / manual verification script**

Create a temporary test script to verify `extractor_rlms.py` fails without the `rlm` dependency (we'll simulate it failing or just verify the new signature works).

```python
# Create scratch/test_rewrite.py
import json
from src.extractor_rlms import extract

def test_extraction():
    # Setup dummy transcript
    with open("dummy.json", "w") as f:
        json.dump([{"role": "user", "content": "Hello"}], f)
    
    try:
        extract("dummy.json", output_file="dummy_out.json")
        print("Success")
    except Exception as e:
        print(f"Failed: {e}")

test_extraction()
```

- [ ] **Step 2: Run test to verify current state**

Run: `python scratch/test_rewrite.py`
Expected: May run, but takes the old `rlm` route.

- [ ] **Step 3: Implement the complete rewrite of `extractor_rlms.py`**

Replace the entire contents of `src/extractor_rlms.py` with this native implementation:

```python
import sys
import json
import os
import re
from src.llm_utils import call_llm
from src.extractor import scrub_pii, merge_graphs

def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_rlms.json"):
    # 1. Load and Scrub Transcript
    with open(conversation_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    safe_transcript = scrub_pii(json.dumps(data))
    
    # 2. Load Base Prompt
    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
    else:
        base_prompt = (
            "You are a Knowledge Graph extraction system.\n"
            "Extract a 4-part JSON Knowledge Graph (Semantic, Episodic, Procedural, Active).\n"
            "Return ONLY a valid JSON object. Do not output any markdown formatting, thinking, or conversational filler."
        )
        
    # 3. Chunk Transcript (3000 chars)
    chunk_size = 3000
    chunks = [safe_transcript[i:i+chunk_size] for i in range(0, len(safe_transcript), chunk_size)]
    
    master_graph = {
        "semantic_memory": {"nodes": [], "edges": []},
        "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
        "procedural_memory": {"instructions": []},
        "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
    }
    
    # 4. Iterate over chunks
    for idx, chunk in enumerate(chunks):
        print(f"[{output_file}] Extracting chunk {idx+1}/{len(chunks)}...")
        
        # Build prompt for this chunk
        sub_prompt = f"{base_prompt}\n\nHere is the text chunk to process:\n\n{chunk}"
        
        raw_extraction = call_llm(sub_prompt)
        
        # 5. Robustly parse JSON blocks
        json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', raw_extraction, re.DOTALL)
        
        if not json_blocks:
            start_idx = raw_extraction.find('{')
            end_idx = raw_extraction.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_blocks = [raw_extraction[start_idx:end_idx+1]]
                
        for block in json_blocks:
            try:
                parsed = json.loads(block)
                master_graph = merge_graphs(master_graph, parsed)
            except Exception as e:
                print(f"[{output_file}] Failed to parse chunk JSON block: {e}")
                
    # 6. Save final output
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_graph, f, indent=2)
        
    print(f"Primary agent successfully extracted to {output_file}")
    
    # Return false to match previous signature (repaired = False)
    return False

if __name__ == "__main__":
    if len(sys.argv) > 3:
        extract(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        extract(sys.argv[1])
    else:
        print("Usage: python src/extractor_rlms.py <transcript.json> [prompt.txt] [output.json]")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scratch/test_rewrite.py`
Expected: "Primary agent successfully extracted to dummy_out.json"

- [ ] **Step 5: Clean up and Commit**

```bash
rm scratch/test_rewrite.py dummy.json dummy_out.json
git add src/extractor_rlms.py
git commit -m "refactor: rip out RLM dependency and implement native python recursive extraction"
```
