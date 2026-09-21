# Fix Missing Schemas and Graph Merging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the `kg_rlms`, `kg_propositional`, and `kg_propositional_v2` extractors which are currently outputting empty graphs due to missing JSON schemas in their prompts and incompatible merging logic in the Python orchestrator.

**Architecture:** 
1. The base prompts (`propositional_kg.txt`, `propositional_v2_kg.txt`, and the default string in `extractor_recursive.py`) still contain remnants of the deprecated `RLM` sandbox architecture, and most importantly, fail to define the exact JSON keys required (`semantic_memory`, etc). We will rewrite them as pure text extraction prompts that explicitly declare the expected JSON structure.
2. The `merge_graphs` function currently hardcodes `CognitiveGraphV1` keys (`semantic_memory`, etc). We will add logic to natively detect and merge `CognitiveGraphV2` structures (`Semantic`, `Episodic`, etc) if present.

**Tech Stack:** Python, JSON

## Global Constraints
- Preserve `CognitiveGraphV1` and `CognitiveGraphV2` structural validation logic (do not modify `src/models.py`).

---

### Task 1: Update `merge_graphs` to support V2 Schema

**Files:**
- Modify: `src/extractor.py:22-31`

**Interfaces:**
- Consumes: A `master` dictionary and `new_data` dictionary representing either V1 or V2 graphs.
- Produces: An updated `master` dictionary with appended elements.

- [ ] **Step 1: Write the failing test**

```python
# scratch/test_merge.py
from src.extractor import merge_graphs

def test_v2_merge():
    master = {"Semantic": [], "Episodic": [], "Procedural": [], "Active": []}
    new_data = {"Semantic": [{"subject": "A", "relation": "B", "object": "C"}]}
    res = merge_graphs(master, new_data)
    assert len(res["Semantic"]) == 1, "Failed to merge V2 semantic nodes"
    print("Pass")

test_v2_merge()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scratch/test_merge.py`
Expected: `KeyError: 'semantic_memory'` or assertion failure.

- [ ] **Step 3: Write minimal implementation**

Modify `merge_graphs` in `src/extractor.py` to handle both V1 and V2:

```python
def merge_graphs(master, new_data):
    if not new_data: return master
    
    # Handle V1 Schema
    if "semantic_memory" in master or "semantic_memory" in new_data:
        if "semantic_memory" not in master:
            master = {
                "semantic_memory": {"nodes": [], "edges": []},
                "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
                "procedural_memory": {"instructions": []},
                "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
            }
        sem = new_data.get("semantic_memory", {})
        master["semantic_memory"]["nodes"].extend(sem.get("nodes", []))
        master["semantic_memory"]["edges"].extend(sem.get("edges", []))
        ep = new_data.get("episodic_ledger", {})
        master["episodic_ledger"]["events"].extend(ep.get("events", []))
        master["episodic_ledger"]["decisions"].extend(ep.get("decisions", []))
        master["episodic_ledger"]["rejected_branches"].extend(ep.get("rejected_branches", []))
        proc = new_data.get("procedural_memory", {})
        master["procedural_memory"]["instructions"].extend(proc.get("instructions", []))
        # Optional: handle active state if needed, usually string overwrite
    
    # Handle V2 Schema
    elif "Semantic" in master or "Semantic" in new_data or "semantic" in new_data:
        if "Semantic" not in master:
            master = {"Semantic": [], "Episodic": [], "Procedural": [], "Active": []}
        
        for key in ["Semantic", "Episodic", "Procedural", "Active"]:
            # Check both TitleCase and lowercase
            items = new_data.get(key, new_data.get(key.lower(), []))
            if isinstance(items, list):
                master.setdefault(key, []).extend(items)
            elif isinstance(items, dict):
                # Failsafe if it outputs a dict instead of a list
                master.setdefault(key, []).extend(items.values())
                
    return master
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scratch/test_merge.py`
Expected: `Pass`

- [ ] **Step 5: Commit**
```bash
rm scratch/test_merge.py
git add src/extractor.py
git commit -m "fix: update merge_graphs to dynamically support V1 and V2 schema merging"
```

---

### Task 2: Refactor Prompt Templates

**Files:**
- Modify: `src/extractor_recursive.py`
- Modify: `src/prompts/propositional_kg.txt`
- Modify: `src/prompts/propositional_v2_kg.txt`

- [ ] **Step 1: Fix `extractor_recursive.py` base prompt**
Update the default `base_prompt` in the `else:` block to include the explicit V1 schema example, and initialize `master_graph` intelligently depending on the prompt type.

```python
# In src/extractor_recursive.py
    else:
        base_prompt = (
            "You are a Knowledge Graph extraction system.\n"
            "Extract a 4-part JSON Knowledge Graph (Semantic, Episodic, Procedural, Active).\n"
            "Return ONLY a valid JSON object. Do not output any markdown formatting, thinking, or conversational filler.\n"
            "Example Format: {\"semantic_memory\": {\"nodes\": [], \"edges\": []}, \"episodic_ledger\": {\"events\": [], \"decisions\": [], \"rejected_branches\": []}, \"procedural_memory\": {\"instructions\": []}, \"active_state\": {\"current_goal\": \"\", \"blockers\": [], \"next_action\": \"\"}}"
        )
        
    # 3. Chunk Transcript
    chunk_size = 3000
    chunks = [safe_transcript[i:i+chunk_size] for i in range(0, len(safe_transcript), chunk_size)]
    
    # Intelligently initialize master graph depending on expected schema
    if prompt_file and 'v2' in prompt_file:
        master_graph = {"Semantic": [], "Episodic": [], "Procedural": [], "Active": []}
    else:
        master_graph = {
            "semantic_memory": {"nodes": [], "edges": []},
            "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
            "procedural_memory": {"instructions": []},
            "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
        }
```

- [ ] **Step 2: Rewrite `propositional_kg.txt`**
Overwrite it with purely prompt-based extraction instructions matching V1.

```text
You are a Knowledge Graph extraction system.
Your goal is to extract a 4-part Knowledge Graph (Semantic, Episodic, Procedural, Active), but the contents MUST be constructed strictly out of dense, verbatim factual Propositions (atomic, self-contained factual statements).

Return ONLY a valid JSON object with the exact structure below. Do not output any markdown formatting, thinking, or conversational filler. Output ONLY raw JSON.

Example Format: 
{
  "semantic_memory": {"nodes": [], "edges": []}, 
  "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []}, 
  "procedural_memory": {"instructions": []}, 
  "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
}
```

- [ ] **Step 3: Rewrite `propositional_v2_kg.txt`**
Overwrite it with purely prompt-based extraction instructions matching V2.

```text
You are a Knowledge Graph extraction system.
Your goal is to extract a 4-part Cognitive Knowledge Graph (Semantic, Episodic, Procedural, Active). 
However, the contents inside each bucket MUST be formatted as strict Triples `{"subject": "...", "relation": "...", "object": "..."}`.
For the Episodic bucket, you MUST include a chronological `"step"` integer to preserve narrative flow.

Return ONLY a valid JSON object with the exact structure below. Do not output any markdown formatting, thinking, or conversational filler. Output ONLY raw JSON.

Example Format:
{
  "Semantic": [
    {"subject": "User", "relation": "possesses_trait", "object": "ENTJ personality"}
  ],
  "Episodic": [
    {"step": 1, "subject": "User", "relation": "expressed_skepticism_about", "object": "unquantifiable metrics"}
  ],
  "Procedural": [
    {"subject": "Taste Evaluation", "relation": "requires", "object": "Sensory acuity"}
  ],
  "Active": [
    {"subject": "AI", "relation": "is_currently_addressing", "object": "User's need for objective standards"}
  ]
}
```

- [ ] **Step 4: Commit**
```bash
git add src/extractor_recursive.py src/prompts/ src/extractor.py
git commit -m "fix: refactor prompts and python script to successfully merge schemas"
```
